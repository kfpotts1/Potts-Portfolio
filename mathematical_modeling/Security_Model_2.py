# Airport TSA throughput model - Kenneth Potts

# This is a model built in python to model throughput at airport TSA lines with the
# intention of gaining insight into a redesign and optimization of the current system.

# This code was written in a matter of hours as this was for a 3 day mathematical modeling
# competition, therefore it is significantly lacking in comments. I will revisit this code
# and add appropriate commenting and documentation when I have additional time.


import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import matplotlib.pyplot as plt
# import datetime
import scipy.stats as stats
from matplotlib import style
from tabulate import tabulate
from Queue import Queue


class Durations:
    def __init__(self, pre_check_pct=0.5, metal_detector_pct=0.33, force_pre_check=None):
        d_data = pd.read_pickle('data/D_data.p')
        self.arrivals_reg = d_data['Regular Pax Arrival Times'].copy().dropna()
        self.arrivals_reg_deltas = self.arrivals_reg.diff()[1:]
        self.arrivals_TSA_pre = d_data['TSA Pre-Check Arrival Times'].copy().dropna()
        self.arrivals_TSA_pre_deltas = self.arrivals_TSA_pre.diff()[1:]

        doc_check_deltas_1 = d_data['ID Check Process Time 1'].copy().dropna()
        doc_check_deltas_2 = d_data['ID Check Process Time 2'].copy().dropna()
        self.doc_check_deltas = doc_check_deltas_1.append(doc_check_deltas_2)

        self.mmw_stamps = d_data['Milimeter Wave Scan times'].copy().dropna()
        self.mmw_deltas = self.mmw_stamps.diff()[1:]

        self.x_ray_scan_1_stamps = d_data['X-Ray Scan Time'].copy().dropna()
        self.x_ray_scan_2_stamps = d_data['X-Ray Scan Time.1'].copy().dropna()

        self.x_ray_scan_deltas = self.x_ray_scan_1_stamps.diff()[1:].append(self.x_ray_scan_2_stamps.diff()[1:])

        self.belt_proper_scan_deltas = d_data['Time to get scanned property'].copy()

        self.pre_check_pct = pre_check_pct
        self.metal_detector_pct = metal_detector_pct
        self.false_alarm_rate = 0.3
        self.pre_check_rate = 0.45
        self.random_screen_rate = 0.05
        self.force_pre_check = force_pre_check

    def gen_arrival_reg_delta(self):
        return np.random.choice(self.arrivals_reg_deltas)

    def gen_arrival_TSA_PRE_delta(self):
        return np.random.choice(self.arrivals_TSA_pre_deltas)

    def gen_doc_check_delta(self):
        return np.random.choice(self.doc_check_deltas)

    def gen_mmw_delta(self):
        return np.random.choice(self.mmw_deltas)

    def gen_x_ray_scan_delta(self):
        return np.random.choice(self.x_ray_scan_deltas)

    def gen_belt_proper_scan_delta(self):
        return np.random.choice(self.belt_proper_scan_deltas)

    def set_pre_check_pct(self, pct):
        self.pre_check_pct = pct

    def gen_zone_d_screen_time(self):
        return stats.chi.rvs(df=3, loc=0, scale=36, size=1).astype(int)[0]

    def gen_bin_placement_time(self):
        return stats.chi.rvs(df=3, loc=0, scale=8, size=1).astype(int)[0]

    def gen_zone_c_screen_time(self):
        return stats.chi.rvs(df=3, loc=0, scale=9, size=1).astype(int)[0]

    def gen_random_screen_time(self):
        return stats.chi.rvs(df=3, loc=0, scale=10, size=1)

    def gen_pre_check_status(self):
        if self.force_pre_check is None:
            pre_check_status = False
            if np.random.binomial(1, self.pre_check_rate) == 1:
                pre_check_status = True
            return pre_check_status
        else:
            return self.force_pre_check


class BinItem:
    def __init__(self, owner):
        self.location = 0
        self.owner = owner


class Person:
    def __init__(self, ID, durations, pre_check):
        """
        creates a person object.

        Person object holds a list of bins, a Series with wait times, and a series with processing times.

        Parameters:
        -------------
            ID : int
                Person number identifier, assigned to person by generator
            wait_line_areas : list of strings
                list of the names of all the lines where the
            processing_area : list of strings
                list of the names of the processing stations

        """
        self.durations = durations

        self.false_alarm_rate = self.durations.false_alarm_rate
        self.random_screen_rate = self.durations.random_screen_rate

        self.false_alarm = False
        self.random_selection = False
        if np.random.binomial(1, self.false_alarm_rate) == 1:
            self.false_alarm = True
        # random selection
        elif np.random.binomial(1, self.random_screen_rate) == 1:
            self.random_selection = True

        self.ID = ID
        self.scanner_used = None
        self.through_body_scan = False
        self.location = None
        self.time_remaining = None
        self.current_time_waiting = 0
        self.side = None

        self.pre_check = pre_check

        if self.pre_check:
            num_bins = stats.chi.rvs(df=3, loc=0, scale=2, size=1).astype(int)[0]
        else:
            num_bins = stats.chi2.rvs(df=3, loc=0, scale=1, size=1).astype(int)[0]
        # Generates randomly the number of bins
        # integers from chi2
        self.num_bins = num_bins.astype(int)
        # list of bins required by person
        self.bins_off_belt = [BinItem(self) for _ in range(self.num_bins)]
        self.bins_on_belt = []

        self.wait_times = Series()
        self.wait_times.name = 'wait_times'
        self.process_times = Series()
        self.process_times.name = 'process_times'


class ZoneC:
    def __init__(self, durations):
        self.belt_lines = None
        self.name = 'zone_c'
        self.zone_d = None
        self.people = []
        self.durations = durations
        self.stats_collector = None

    def set_connections(self, belt_lines, zone_d, stats_collector):
        if type(belt_lines) != list:
            belt_lines = [belt_lines]
        self.belt_lines = belt_lines
        self.zone_d = zone_d
        self.stats_collector = stats_collector

    def pull(self):
        for line in self.belt_lines:
            persons = line.push(self.name)
            for person in persons:
                if person is not None:
                    self.people.append(person)
                    person.location = self
                    person.process_times[self.name] = self.durations.gen_zone_c_screen_time() * person.num_bins
        persons = self.zone_d.push()
        for person in persons:
            if person is not None:
                self.people.append(person)
                person.process_times[self.name] = self.durations.gen_zone_c_screen_time() * person.num_bins
                person.location = self

    def iterate(self, second):
        for person in self.people:
            if person.time_remaining != 0:
                person.time_remaining -= 1

    def push(self):
        to_push = []
        not_push = []
        for person in self.people:
            if person.time_remaining == 0:
                to_push.append(person)
                person.location = None
            else:
                not_push.append(person)
        self.people = not_push
        return to_push

    def count(self):
        return len(self.people)

    def is_empty(self):
        return self.count() == 0


class ZoneD:
    # multiple additional screenings
    def __init__(self, durations, num_add_screens=1):
        self.num_add_screens = num_add_screens
        self.to_screen = []
        self.post_screen = []
        self.in_screening = []
        self.durations = durations
        self.name = 'zone_d'
        self.zone_c = None
        self.post_scan_lines = None

    def set_connections(self, post_scan_lines, zone_c):
        if type(post_scan_lines) != list:
            post_scan_lines = [post_scan_lines]
        self.post_scan_lines = post_scan_lines
        self.zone_c = zone_c

    def add_to_screening_queue(self, person):
        self.to_screen.append(person)
        person.wait_times[self.name] = 0

    def send_to_station(self, person):
        if len(self.in_screening) < self.num_add_screens:
            self.in_screening.append(person)
            process_time = self.durations.gen_zone_d_screen_time()
            person.time_remaining = process_time
            person.process_times[self.name] = process_time

    def add_to_post_screen(self, person):
        self.post_screen.append(person)

    def push(self):
        people = self.post_screen
        self.post_screen = []
        return people

    def pull(self):
        for line in self.post_scan_lines:
            people = line.push(self.name)
            for person in people:
                self.add_to_screening_queue(person)

    def iterate(self, second):
        stays = []
        leaves = []
        for person in self.in_screening:
            if person.time_remaining == 0:
                leaves.append(person)
            else:
                if person.time_remaining > 0:
                    person.time_remaining -= 1
                stays.append(person)

        for person in leaves:
            self.add_to_post_screen(person)
        self.in_screening = stays
        if len(self.in_screening) < self.num_add_screens and len(self.to_screen) != 0:
            self.send_to_station(self.to_screen.pop(0))

        for person in self.to_screen:
            person.wait_times[self.name] += 1


class PostScanLine:
    def __init__(self, side):
        self.line = []
        self.side = side
        self.name = 'post_scan_line'
        if side == 'left':
            self.left = True
        else:
            self.left = False

        self.zone_c = None
        self.zone_d = None
        self.body_scanners = None
        self.x_ray_belt = None

    def set_connections(self, zone_c, zone_d, body_scanners, x_ray_belt):
        self.zone_c = zone_c
        self.zone_d = zone_d
        if type(body_scanners) != list:
            body_scanners = [body_scanners]
        self.body_scanners = body_scanners
        self.x_ray_belt = x_ray_belt

    def pull(self):
        for scanner in self.body_scanners:
            person = scanner.push(self.side)
            if person is not None:
                self.line.append(person)
                person.location = self
                person.wait_times[self.name] = 0

    def push(self, zone):
        stays = []
        leaves = []
        if zone == 'zone_c':
            for person in self.line:
                if not person.false_alarm and len(person.bins_on_belt) == 0:
                    leaves.append(person)
                    person.location = None
                else:
                    stays.append(person)
        elif zone == 'zone_d':
            for person in self.line:
                if person.false_alarm and len(person.bins_on_belt) == 0:
                    leaves.append(person)
                    person.location = None
                else:
                    stays.append(person)
        else:
            raise ValueError('invalid zone')
        self.line = stays
        return leaves

    def iterate(self, second):
        for person in self.line:
            person.wait_times[self.name] += 1
            self.x_ray_belt.person_get_available_bins(person)

    def is_empty(self):
        return len(self.line) == 0

    def get_count(self):
        return len(self.line)


class XRayBelt:
    def __init__(self, durations, pre_scan_spots=5):
        self.scanned_bins = []  # 4 bins after begin scanned
        self.scanned_bins_max = 4
        self.scanning = None
        self.pre_scan_spots = pre_scan_spots
        self.pre_scan_q = Queue(maxsize=self.pre_scan_spots)
        self.durations = durations
        self.next_scan_time = self.durations.gen_x_ray_scan_delta()
        self.idle_seconds = []
        self.name = 'x_ray_belt'
        self.bin_placement = None

    def set_connections(self, bin_placement):
        self.bin_placement = bin_placement

    def iterate(self, second):
        if self.next_scan_time == 0:
            self.next_scan_time = self.durations.gen_x_ray_scan_delta()
            # move from scanning to scanned
            if len(self.scanned_bins) < self.scanned_bins_max:
                if self.scanning is not None:
                    self.scanned_bins.append(self.scanning)
                if not self.pre_scan_q.empty():
                    self.scanning = self.pre_scan_q.get()
                else:
                    self.scanning = None

        else:
            if self.next_scan_time > 0:
                self.next_scan_time -= 1
        if self.scanning is None and self.pre_scan_q.empty():
            self.idle_seconds.append(second)

    def get_open_spots(self):
        return self.pre_scan_spots - self.pre_scan_q.qsize()

    def has_vacancy(self):
        return self.get_open_spots() != 0

    def person_get_available_bins(self, person):
        bins_stay = []
        for bin_item in self.scanned_bins:
            if bin_item.owner == person:
                person.bins_on_belt.remove(bin_item)
                person.bins_off_belt.append(bin_item)
            else:
                bins_stay.append(bin_item)
        self.scanned_bins = bins_stay

    def place_bin(self, bin_item):
        if self.has_vacancy():
            self.pre_scan_q.put(bin_item)
        else:
            raise RuntimeError('Bin placement failed on x-ray belt')


class BinPlacement:
    def __init__(self, side, durations):
        self.belt_line = None
        self.pre_scan_line = None
        self.x_ray_belt = None
        self.side = side
        self.person = None
        self.durations = durations
        self.bin_time = 0
        self.name = 'bin_placement'

    def set_connections(self, belt_line, pre_scan_line, x_ray_belt):
        self.x_ray_belt = x_ray_belt
        self.pre_scan_line = pre_scan_line
        self.belt_line = belt_line

    def push(self):
        if self.person is not None:
            if len(self.person.bins_on_belt) == self.person.num_bins:
                curr_person = self.person
                self.person = None
                self.bin_time = 0
                curr_person.location = None
                return curr_person
        else:
            return None

    def pull(self):
        if self.person is None:
            person = self.belt_line.push()
            if person is not None:
                self.person = person
                self.person.location = self
                self.person.side = self.side
                self.bin_time = self.durations.gen_bin_placement_time()
                self.person.process_times[self.name] = self.bin_time * self.person.num_bins

    def iterate(self, second):
        if self.person is not None:
            if (len(self.person.bins_on_belt) < self.person.num_bins) and (len(self.person.bins_off_belt) > 0):
                if self.x_ray_belt.has_vacancy() and self.bin_time == 0:
                    bin_to_place = self.person.bins_off_belt.pop(0)
                    self.x_ray_belt.place_bin(bin_to_place)
                    self.person.bins_on_belt.append(bin_to_place)
                else:
                    if self.bin_time != 0:
                        self.bin_time -= 1


class Scanner:
    def __init__(self, durations, name):
        self.person = None
        self.idle_seconds = []
        self.durations = durations
        self.pre_scan_line = None
        self.post_scan_lines = None
        self.name = name

    def set_connections(self, pre_scan_line, post_scan_lines):
        self.pre_scan_line = pre_scan_line
        self.post_scan_lines = post_scan_lines

    def is_empty(self):
        return self.person is None

    def is_in_use(self):
        return not self.is_empty()

    def push(self, side):
        person_to_push = None
        if self.person is not None:
            if self.person.time_remaining == 0:
                if self.person.side == side:
                    person_to_push = self.person
                    person_to_push.location = None
                    self.person = None
        return person_to_push

    def pull(self):
        if self.person is None:
            self.person = self.pre_scan_line.push()
            if self.person is not None:
                self.person.scanner_used = self.name
                self.person.location = self
                if self.name == 'mmw':
                    self.person.time_remaining = self.durations.gen_mmw_delta()
                elif self.name == 'metal_detector':
                    self.person.time_remaining = self.durations.gen_mmw_delta() * self.durations.metal_detector_pct
                self.person.process_times['body_scanner'] = self.person.time_remaining

    def iterate(self, second):
        if self.person is not None:
            if self.person.time_remaining != 0:
                self.person.time_remaining -= 1
        else:
            self.idle_seconds.append(second)


class PreScanLine:
    def __init__(self, maxsize=8):
        self.name = 'pre_scan_line'
        self.line = []
        self.maxsize = maxsize
        self.scanner = None
        self.bin_placement = None

    def set_connections(self, scanner, bin_placement):
        self.bin_placement = bin_placement
        self.scanner = scanner

    def is_empty(self):
        return len(self.line) == 0

    def is_full(self):
        return len(self.line) == self.maxsize

    def get_count(self):
        return len(self.line)

    def push(self):
        if not self.is_empty():
            person_to_push = self.line.pop(0)
            person_to_push.location = None
            return person_to_push

    def pull(self):
        if not self.is_full():
            person = self.bin_placement.push()
            if person is not None:
                self.line.append(person)
                person.location = self
                person.wait_times[self.name] = 0

    def iterate(self, second):
        for person in self.line:
            person.wait_times[self.name] += 1


class BeltLine:
    def __init__(self, maxsize=20):
        self.line = []
        self.maxsize = maxsize
        self.pre_process = None
        self.bin_placement = None
        self.name = 'x_ray_line'

    def set_connections(self, pre_process, bin_placement):
        self.bin_placement = bin_placement
        self.pre_process = pre_process

    def is_empty(self):
        return len(self.line) == 0

    def is_full(self):
        return len(self.line) == self.maxsize

    def get_count(self):
        return len(self.line)

    def push(self):
        if not self.is_empty():
            person_to_push = self.line.pop(0)
            person_to_push.location = None
            # print 'found ', person_to_push.ID ############################################################
            return person_to_push

    def pull(self):
        if not self.is_full():
            person = self.pre_process.push(self)
            if person is not None:
                # print 'found ', person.ID  ############################################################
                person.location = self
                person.wait_times[self.name] = 0
                self.line.append(person)

    def iterate(self, second):
        for person in self.line:
            person.wait_times[self.name] += 1


class DocCheck:
    def __init__(self, durations):
        self.person = None
        self.idle_seconds = []
        self.durations = durations
        self.pre_doc_check_process = None
        self.post_doc_check_process = None
        self.name = 'doc_check'

    def set_connections(self, pre_doc_check_process, post_doc_check_process):
        self.pre_doc_check_process = pre_doc_check_process
        self.post_doc_check_process = post_doc_check_process

    def is_empty(self):
        return self.person is None

    def is_in_use(self):
        return not self.is_empty()

    def push(self, out):
        person_to_push = None
        if self.person is not None:
            if self.person.time_remaining == 0:
                person_to_push = self.person
                person_to_push.location = None
                self.person = None
        return person_to_push

    def pull(self):
        if self.person is None:
            self.person = self.pre_doc_check_process.push(self)
            if self.person is not None:
                self.person.location = self
                self.person.time_remaining = self.durations.gen_doc_check_delta()
                self.person.process_times[self.name] = self.person.time_remaining

    def iterate(self, second):
        if self.person is not None:
            if self.person.time_remaining != 0:
                self.person.time_remaining -= 1
        else:
            self.idle_seconds.append(second)


class FirstLine:
    def __init__(self, pre_check=False):
        self.line = []
        self.out_process = None
        self.in_process = None
        self.name = 'first_line'
        self.pre_check = pre_check

    def set_connections(self, in_process, out_process):
        self.in_process = in_process
        self.out_process = out_process

    def is_empty(self):
        return len(self.line) == 0

    def get_count(self):
        return len(self.line)

    def push(self, out):
        if not self.is_empty():
            person_to_push = self.line.pop(0)
            person_to_push.location = None
            return person_to_push

    def pull(self):
        people = self.in_process.push(self)
        if type(people) != list:
            people = [people]
        for person in people:
            if person is not None:
                person.location = self
                person.wait_times[self.name] = 0
                self.line.append(person)

    def iterate(self, second):
        for person in self.line:
            person.wait_times[self.name] += 1


class DocIntoBeltLineFeeder:
    def __init__(self, minimize_out=False):
        self.name = 'feeder'
        self.in_processes = None
        self.out_processes = None
        self.next_out_process = None
        self.person = None
        self.next_in_process = None
        self.minimize_out = minimize_out

    def set_connections(self, in_processes, out_processes):
        if type(in_processes) != list:
            in_processes = [in_processes]
        if type(out_processes) != list:
            out_processes = [out_processes]
        self.in_processes = in_processes
        self.out_processes = out_processes
        self.next_out_process = self.out_processes[0]
        self.next_in_process = self.in_processes[0]

    def calc_next_out_process(self):
        if self.minimize_out:
            curr_min = 0
            for location in self.out_processes:
                val = location.get_count()
                if val <= curr_min:
                    self.next_out_process = location
        else:
            self.next_out_process = self.out_processes[0]

        # to eliminate always choosing a single row from many
        np.random.shuffle(self.out_processes)

    def calc_next_in_process(self):
        for location in self.in_processes:
            if location.is_empty():
                self.next_in_process = location
        # to eliminate always choosing a single row from many
        np.random.shuffle(self.in_processes)

    def pull(self):
        if self.person is None:
            self.person = self.next_in_process.push(self)

    def push(self, out):
        if out == self.next_out_process:
            person_out = self.person
            self.person = None
            return person_out

    def iterate(self, second):
        self.calc_next_in_process()
        self.calc_next_out_process()


class DocFeeder:
    def __init__(self, minimize_in=False):
        self.name = 'feeder'
        self.in_processes = None
        self.out_processes = None
        self.next_out_process = None
        self.person = None
        self.next_in_process = None
        self.minimize_in = minimize_in

    def set_connections(self, in_processes, out_processes):
        if type(in_processes) != list:
            in_processes = [in_processes]
        if type(out_processes) != list:
            out_processes = [out_processes]
        self.in_processes = in_processes
        self.out_processes = out_processes
        self.next_out_process = self.out_processes[0]
        self.next_in_process = self.in_processes[0]

    def calc_next_out_process(self):
        for location in self.out_processes:
            if location.is_empty():
                self.next_out_process = location

        # to eliminate always choosing a single row from many
        np.random.shuffle(self.out_processes)

    def calc_next_in_process(self):
        if self.minimize_in:
            curr_min = 0
            for location in self.in_processes:
                val = location.get_count()
                if val <= curr_min:
                    curr_min = val
                    self.next_in_process = location
        else:
            self.next_in_process = self.in_processes[0]
        # to eliminate always choosing a single row from many
        np.random.shuffle(self.in_processes)

    def pull(self):
        if self.person is None:
            self.person = self.next_in_process.push(self)

    def push(self, out):
        if out == self.next_out_process:
            person_out = self.person
            self.person = None
            return person_out

    def iterate(self, second):
        self.calc_next_in_process()
        self.calc_next_out_process()


class StatsCollector:
    def __init__(self):
        self.in_process = None
        self.people_stats = None
        self.q = Queue()
        self.stored_person = None
        self.idle_times = None

    def set_connections(self, in_process):
        self.in_process = in_process

    def pull(self):
        persons = self.in_process.push()
        if persons is not None:
            if type(persons) != list:
                persons = [persons]
            for person in persons:
                if person is not None:
                    self.q.put(person)

    def iterate(self, second):
        while not self.q.empty():
            person = self.q.get()
            s_process = person.process_times
            s_wait = person.wait_times

            df_process = DataFrame(s_process)
            df_wait = DataFrame(s_wait)
            df_process = df_process.T

            df_wait = df_wait.T

            # Set up columns and indexes
            label_process = df_process.index.tolist()[0]
            label_wait = df_wait.index.tolist()[0]

            columns_process = df_process.columns.tolist()
            columns_wait = df_wait.columns.tolist()
            upper_process = [label_process] * len(columns_process)
            upper_wait = [label_wait] * len(columns_wait)
            tuples_process = list(zip(upper_process, columns_process))
            tuples_wait = list(zip(upper_wait, columns_wait))
            df_process.columns = pd.MultiIndex.from_tuples(tuples_process)
            df_wait.columns = pd.MultiIndex.from_tuples(tuples_wait)
            df_process.index = range(len(df_process))
            df_wait.index = range(len(df_wait))

            # merge to full DataFrame
            person_stats = pd.concat([df_process, df_wait], axis=1)

            person_stats.loc[0, ('attributes', 'ID')] = person.ID
            person_stats.loc[0, ('attributes', 'num_bins')] = person.num_bins
            person_stats.loc[0, ('attributes', 'scanner_used')] = person.scanner_used
            person_stats.loc[0, ('attributes', 'pre_check_status')] = person.pre_check
            person_stats.loc[0, ('attributes', 'randomly_selected')] = person.random_selection
            person_stats.loc[0, ('attributes', 'failed_scan')] = person.false_alarm
            person_stats.loc[0,('totals', 'process_time')] = \
                person_stats.loc[0, ('totals', 'process_time')] = \
                person_stats.loc[0:, ('process_times')].sum(axis=1).values[0]
            person_stats.loc[0, ('totals', 'wait_time')] = \
                person_stats.loc[0:, ('wait_times')].sum(axis=1).values[0]
            person_stats.loc[0, ('totals', 'total_time')] = \
                person_stats.loc[0:, ('totals', 'process_time')].values[0] + \
                person_stats.loc[0:, ('totals', 'wait_time')].values[0]

            self.people_stats = pd.concat([self.people_stats, person_stats], ignore_index=True)
            self.people_stats.fillna(value=0, inplace=True)

            del person
            
    def calc_idle_times(self):
        pass


class Generator:
    def __init__(self, durations, separate_pre_check=False):
        self.out_processes = None
        self.durations = durations
        self.countdown = 0
        self.person_count = 0
        self.separate_pre_check = separate_pre_check
        self.next_pre_check_status = False

    def set_connections(self, out_processes):
        if type(out_processes) != list:
            out_processes = [out_processes]
        self.out_processes = out_processes

    def push(self, out):
        if (not self.separate_pre_check) and (self.countdown == 0):
            person = Person(self.person_count, self.durations, self.next_pre_check_status)
            self.person_count += 1
            self.next_pre_check_status = self.durations.gen_pre_check_status()
            if self.next_pre_check_status:
                self.countdown = self.durations.gen_arrival_TSA_PRE_delta()
            else:
                self.countdown = self.durations.gen_arrival_reg_delta()
            return person
        elif self.countdown == 0:
            if out.pre_check == self.next_pre_check_status:
                person = Person(self.person_count, self.durations, self.next_pre_check_status)
                self.person_count += 1
                self.next_pre_check_status = self.durations.gen_pre_check_status()
                self.countdown = self.durations.gen_arrival_reg_delta()
                return person

    def iterate(self, second):
        if self.countdown != 0:
            self.countdown -= 1

    def pull(self):
        pass


class Model:
    def __init__(self, seed=None, model_style='single_lane', force_pre_check=None):
        if seed is not None:
            np.random.seed(seed)
        self.model_style = model_style
        self.force_pre_check = force_pre_check
        if self.model_style == 'single_lane':
            self.durations = Durations(force_pre_check=self.force_pre_check)
            self.generator = Generator(self.durations)
            self.first_line = FirstLine()
            self.doc_check = DocCheck(self.durations)
            self.belt_line = BeltLine()
            self.bin_placement = BinPlacement('right', self.durations)
            self.pre_scan_line = PreScanLine()
            self.x_ray_belt = XRayBelt(self.durations)
            self.scanner = Scanner(self.durations, 'mmw')
            self.post_scan_line = PostScanLine('right')
            self.zone_d = ZoneD(self.durations)
            self.zone_c = ZoneC(self.durations)
            self.stats_collector = StatsCollector()
        elif model_style == 'simple_multi_lane':
            self.durations = Durations(force_pre_check=self.force_pre_check)
            self.generator = Generator(self.durations, separate_pre_check=False)
            self.first_line = FirstLine(pre_check=False)
            self.doc_feeder = DocFeeder(minimize_in=True)  # if not running try False
            self.doc_check_1 = DocCheck(self.durations)
            self.doc_check_2 = DocCheck(self.durations)
            self.belt_line_feeder = DocIntoBeltLineFeeder(minimize_out=True) # Try false if not running
            self.belt_line_1 = BeltLine()
            self.belt_line_2 = BeltLine()
            self.bin_placement_1 = BinPlacement('left', self.durations)
            self.bin_placement_2 = BinPlacement('right', self.durations)
            self.pre_scan_line_1 = PreScanLine()
            self.pre_scan_line_2 = PreScanLine()
            self.x_ray_belt_1 = XRayBelt(self.durations)
            self.x_ray_belt_2 = XRayBelt(self.durations)
            self.scanner_mmw = Scanner(self.durations, 'mmw')
            self.scanner_metal_det = Scanner(self.durations, 'metal_detector')
            self.post_scan_line_1 = PostScanLine('right')
            self.post_scan_line_2 = PostScanLine('right')
            self.zone_d = ZoneD(self.durations)
            self.zone_c = ZoneC(self.durations)
            self.stats_collector = StatsCollector()

    def set_connections(self):
        if self.model_style == 'single_lane':
            self.generator.set_connections(self.first_line)
            self.first_line.set_connections(self.generator, self.doc_check)
            self.doc_check.set_connections(self.first_line, self.belt_line)
            self.belt_line.set_connections(self.doc_check, self.bin_placement)
            self.bin_placement.set_connections(self.belt_line, self.pre_scan_line, self.x_ray_belt)
            self.pre_scan_line.set_connections(self.scanner, self.bin_placement)
            self.x_ray_belt.set_connections(self.bin_placement)
            self.scanner.set_connections(self.pre_scan_line, self.post_scan_line)
            self.post_scan_line.set_connections(self.zone_c, self.zone_d, self.scanner, self.x_ray_belt)
            self.zone_d.set_connections(self.post_scan_line, self.zone_c)
            self.zone_c.set_connections(self.post_scan_line, self.zone_d, self.stats_collector)
            self.stats_collector.set_connections(self.zone_c)
        elif self.model_style == 'simple_multi_lane':

            self.generator.set_connections([self.first_line])
            self.first_line.set_connections(self.generator, self.doc_feeder)
            self.doc_feeder.set_connections([self.first_line],
                                            [self.doc_check_1, self.doc_check_2])
            self.doc_check_1.set_connections(self.doc_feeder, self.belt_line_feeder)
            self.doc_check_2.set_connections(self.doc_feeder, self.belt_line_feeder)
            self.belt_line_feeder.set_connections([self.doc_check_1, self.doc_check_2],
                                                  [self.belt_line_1, self.belt_line_2])
            self.belt_line_1.set_connections(self.belt_line_feeder, self.bin_placement_1)
            self.belt_line_2.set_connections(self.belt_line_feeder, self.bin_placement_2)
            self.bin_placement_1.set_connections(self.belt_line_1, self.pre_scan_line_1, self.x_ray_belt_1)
            self.bin_placement_2.set_connections(self.belt_line_2, self.pre_scan_line_2, self.x_ray_belt_2)
            self.pre_scan_line_1.set_connections(self.scanner_mmw, self.bin_placement_1)
            self.pre_scan_line_2.set_connections(self.scanner_metal_det, self.bin_placement_2)
            self.x_ray_belt_1.set_connections(self.bin_placement_1)
            self.x_ray_belt_2.set_connections(self.bin_placement_2)
            self.scanner_mmw.set_connections(self.pre_scan_line_1, self.post_scan_line_1)
            self.scanner_metal_det.set_connections(self.pre_scan_line_1, self.post_scan_line_1)
            self.post_scan_line_1.set_connections(self.zone_c, self.zone_d,
                                                  [self.scanner_mmw,
                                                   self.scanner_metal_det],
                                                  self.x_ray_belt_1)
            self.post_scan_line_2.set_connections(self.zone_c, self.zone_d,
                                                  [self.scanner_mmw,
                                                   self.scanner_metal_det],
                                                  self.x_ray_belt_2)
            self.zone_d.set_connections([self.post_scan_line_1, self.post_scan_line_2], self.zone_c)
            self.zone_c.set_connections([self.post_scan_line_1, self.post_scan_line_2],
                                        self.zone_d, self.stats_collector)
            self.stats_collector.set_connections(self.zone_c)

    def run_model(self, seconds=2000):
        self.set_connections()
        if self.model_style == 'single_lane':
            for i in range(seconds):
                self.stats_collector.pull()
                self.zone_c.pull()
                self.zone_d.pull()
                self.post_scan_line.pull()
                self.scanner.pull()
                self.pre_scan_line.pull()
                self.bin_placement.pull()
                self.belt_line.pull()
                self.doc_check.pull()
                self.first_line.pull()

                self.stats_collector.iterate(i)
                self.zone_c.iterate(i)
                self.zone_d.iterate(i)
                self.post_scan_line.iterate(i)
                self.scanner.iterate(i)
                self.x_ray_belt.iterate(i)
                self.pre_scan_line.iterate(i)
                self.bin_placement.iterate(i)
                self.belt_line.iterate(i)
                self.doc_check.iterate(i)
                self.first_line.iterate(i)
                self.generator.iterate(i)
        elif self.model_style == 'simple_multi_lane':
            for i in range(seconds):
                self.stats_collector.pull()
                self.zone_c.pull()
                self.zone_d.pull()
                self.post_scan_line_1.pull()
                self.post_scan_line_2.pull()
                self.scanner_mmw.pull()
                self.scanner_metal_det.pull()
                self.pre_scan_line_1.pull()
                self.pre_scan_line_2.pull()
                self.bin_placement_1.pull()
                self.bin_placement_2.pull()
                self.belt_line_1.pull()
                self.belt_line_2.pull()
                self.belt_line_feeder.pull()
                self.doc_check_1.pull()
                self.doc_check_2.pull()
                self.doc_feeder.pull()
                self.first_line.pull()

                self.stats_collector.iterate(i)
                self.zone_c.iterate(i)
                self.zone_d.iterate(i)
                self.post_scan_line_1.iterate(i)
                self.post_scan_line_2.iterate(i)
                self.scanner_mmw.iterate(i)
                self.scanner_metal_det.iterate(i)
                self.pre_scan_line_1.iterate(i)
                self.pre_scan_line_2.iterate(i)
                self.x_ray_belt_1.iterate(i)
                self.x_ray_belt_2.iterate(i)
                self.bin_placement_1.iterate(i)
                self.bin_placement_2.iterate(i)
                self.belt_line_1.iterate(i)
                self.belt_line_2.iterate(i)
                self.belt_line_feeder.iterate(i)
                self.doc_check_1.iterate(i)
                self.doc_check_2.iterate(i)
                self.doc_feeder.iterate(i)
                self.first_line.iterate(i)
                self.generator.iterate(i)

    def summary_stats(self, mode='print', data_head=False):
        if mode == 'return':
            return self.stats_collector.people_stats.describe().T
        elif mode == 'print':
            if data_head:
                print 'Stats Tables Head:'
                print tabulate(self.stats_collector.people_stats.head().T, headers='keys', tablefmt='psql')
            print 'SUMMARY STATISTICS:'
            print tabulate(self.stats_collector.people_stats.drop(('attributes', 'ID'), axis=1).describe().T,
                           headers='keys', tablefmt='psql')

    def summary_plots(self, figsize=(12,6)):
        style.use('fivethirtyeight')
        style.use('seaborn-whitegrid')
        style.use('seaborn-notebook')
        people_stats = self.stats_collector.people_stats
        # Total hists
        f, axarr = plt.subplots(1, 3, figsize=(12, 5))
        axarr[0].hist(people_stats.totals.process_time, bins=15, alpha=0.8)
        axarr[0].set_title('Total Time Spent in Security Checks Per Person')
        axarr[1].hist(people_stats.totals.wait_time, bins=15, alpha=0.8)
        axarr[1].set_title('Total Time Spent Waiting Per Person')
        axarr[2].hist(people_stats.totals.total_time, bins=15, alpha=0.8)
        axarr[2].set_title('Total Time Per Person Through Security')
        for ax in axarr.flatten():
            ax.set_ylabel('Frequency')
            ax.set_xlabel('Seconds')

        # Processing station details
        f, axarr = plt.subplots(1, 3, figsize=figsize)
        axarr[0].plot(people_stats.process_times.doc_check, alpha=0.4, label='Doc Check')
        axarr[0].plot(people_stats.process_times.bin_placement, alpha=0.4, label='Place Bins on Belt')
        axarr[0].plot(people_stats.process_times.body_scanner, alpha=0.4, label='Body Scan')
        axarr[0].plot(people_stats.process_times.zone_c, alpha=0.4, label='Bag Collection and Exit')
        axarr[0].set_title('Time Spent at Processing Station')

        axarr[1].plot(people_stats.wait_times.first_line, alpha=0.6, label='ID Check')
        axarr[1].plot(people_stats.wait_times.x_ray_line, alpha=0.6, label='Bag X-Ray')
        axarr[1].plot(people_stats.wait_times.pre_scan_line, alpha=0.6, label='Body Scan')
        axarr[1].plot(people_stats.wait_times.post_scan_line, alpha=0.6, label='Bag Collection')
        axarr[1].set_title('Time Spent Waiting Before Processing Station')

        axarr[2].plot(people_stats.wait_times.zone_d[people_stats.wait_times.zone_d != 0].values, alpha=0.6,
                         label='Additional Screening Wait Time')
        axarr[2].plot(people_stats.process_times.zone_d[people_stats.process_times.zone_d != 0].values,
                         alpha=0.6, label='Additional Screening Time')
        axarr[2].set_title('Those Flagged For Screening')

        for ax in axarr.flatten():
            ax.set_ylabel('Seconds')
            ax.set_xlabel('Person Number')
            ax.legend(loc='best')

        f, axarr = plt.subplots(1, 2, figsize=figsize)

        axarr[0].plot(people_stats.totals.total_time, alpha=0.6, label='Total Time')
        axarr[0].plot(people_stats.totals.wait_time, alpha=0.6, label='Total Time Waiting')
        axarr[0].plot(people_stats.totals.process_time, alpha=0.6, label='Total Time at Processing Station')
        axarr[0].set_title('Time Spent Per Category For All Travelers')

        axarr[1].plot(people_stats.totals.total_time[~people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Total Time Non Pre-Check')
        axarr[1].plot(people_stats.totals.wait_time[~people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Time Waiting Non Pre-Check')
        axarr[1].plot(people_stats.totals.process_time[~people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Processing Station Time Non Pre-Check')

        axarr[1].plot(people_stats.totals.total_time[people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Total Time Pre-Check')
        axarr[1].plot(people_stats.totals.wait_time[people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Time Waiting Pre-Check')
        axarr[1].plot(people_stats.totals.process_time[people_stats.attributes.pre_check_status].values,
                      alpha=0.6, label='Processing Station Time Pre-Check')

        axarr[1].set_title('Time Spent Per Category by TSA-PreCheck Status')

        for ax in axarr.flatten():
            ax.set_ylabel('Seconds')
            ax.set_xlabel('Person Number')
            ax.legend(loc='best')

        f, axarr = plt.subplots(1, 2, figsize=figsize)

        axarr[0].plot(people_stats.totals.total_time[~people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time')
        axarr[0].plot(people_stats.totals.wait_time[~people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time Waiting')
        axarr[0].plot(people_stats.totals.process_time[~people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time at Processing Station')
        axarr[0].set_title('Time Spent Per Category For Traveler with Failed Scan')

        axarr[1].plot(people_stats.totals.total_time[people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time')
        axarr[1].plot(people_stats.totals.wait_time[people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time Waiting')
        axarr[1].plot(people_stats.totals.process_time[people_stats.attributes.failed_scan].values,
                      alpha=0.5, label='Total Time at Processing Station')
        axarr[1].set_title('Time Spent Per Category For Traveler without Failed Scan')

        for ax in axarr.flatten():
            ax.set_ylabel('Seconds')
            ax.set_xlabel('Person Number')
            ax.legend(loc='best')

if __name__ == "__main__":
    # m1 = Model(seed=321, model_style='single_lane')
    m1 = Model(model_style='simple_multi_lane')
    m1.run_model(seconds=2000)
    m1.summary_stats(data_head=True)
    # m1.summary_plots()

