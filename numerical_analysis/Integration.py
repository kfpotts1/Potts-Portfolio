"""
Numerical Integration Functions: approximate integrals with adaptive quadrature algorithms
"""

from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np
from pandas import DataFrame, Series
import pandas as pd


def quad(func, a, b, tol=1e-5, method='TRAP', adaptive=True, double_nodes=True, visual_mode=False):
    """
    Approximate the integral of function func, on the interval [a,b]
    return the approximation and an upper bound on the error.

    Calls the ad_quad function which uses the an adaptive quadrature method.

    Args:
        func: the function to be integrated (callable)
        a (float): the lower bound of the interval of integration
        b (float): the upper bound of the interval of integration
        tol (float, optional): desired error tolerance, defaults to 1e-5
        method (str, optional): quadrature method to be used, defaults to 'TRAP'
        adaptive (bool, optional): True opts for adaptive quadrature,
                                   false uses standard, defaults to True
        double_nodes (bool, optional): True doubles the amount of nodes at each step,
                                       only used with standard quadrature, defaults to True
        visual_mode (bool, optional): True will produce an interactive plot of nodes,
                                      defaults to False

    Returns:
        Integral Approximation (float): The Approximation of the integral
        Error upper bound (float): An upper bound on the error of the approximation
    """

    def _ad_quad(function, a_1, b_1, tol_1, method_1, total_lines_1, val_dict_1={}):
        """
            Approximate the integral of function func, on the interval [a,b]
            return the approximation and an upper bound on the error.

            Called from quad. This function uses the an adaptive quadrature method.
            This function is called recursively. _ad_quad is defined from
            within quad because it should be only be called from within a_quad
            but must remain separate to perform recursive calls.

            Args:
                function: the function to be integrated (callable)
                a_1 (float): the lower bound of the interval of integration
                b_1 (float): the upper bound of the interval of integration
                tol_1 (float): desired error tolerance, defaults to 1e-6
                method_1 (str): quadrature method to be used, defaults to 'TRAP'
                total_lines_1 (int): the total number of lines run
                val_dict_1 (dict): should be an empty dictionary when first called


            Returns:
                Integral Approximation (float): The Approximation of the integral
                Error upper bound (float): An upper bound on the error of the approximation
                Nodes dictionary (dict): A dictionary of the points used to
                    approximate the integral
                Total lines run (int): The total number of lines run by the function
        """

        line_sum = total_lines_1

        # interval validity
        if a_1 > b_1:
            a_1, b_1 = b_1, a_1

        # common points for all methods:

        mid = (a_1 + b_1) / 2  # midpoint

        val_dict = val_dict_1

        if a_1 in val_dict:
            fa = val_dict[a_1]
        else:
            fa = function(a_1)
            val_dict[a_1] = fa
        if b_1 in val_dict:
            fb = val_dict[b_1]
        else:
            fb = function(b_1)
            val_dict[b_1] = fb
        if mid in val_dict:
            fm = val_dict[mid]
        else:
            fm = function(mid)
            val_dict[mid] = fm

        # Choose Method and calculate

        if method_1 == 'SIMPSON':  # Simpson's rule
            h1 = (b_1 - a_1) / 2  # interval size for approx i_one
            h2 = (b_1 - a_1) / 4  # interval size for approx i_two
            quarter_1 = a_1 + h2
            quarter_3 = mid + h2

            if quarter_1 in val_dict:
                fq_1 = val_dict[quarter_1]
            else:
                fq_1 = function(quarter_1)
                val_dict[quarter_1] = fq_1
            if quarter_3 in val_dict:
                fq_3 = val_dict[quarter_3]
            else:
                fq_3 = function(quarter_3)
                val_dict[quarter_3] = fq_3

            i_one = (h1 / 3) * (fa + (4 * fm) + fb)
            i_two = (h2 / 3) * (fa + (4 * fq_1) + (2 * fm) + (4 * fq_3) + fb)
            max_error = np.abs(i_two - i_one) / 15  # calculates upper bound on
                                                    # error for Simpson's composite

            if max_error < tol_1:
                return i_two, max_error, val_dict, line_sum
            else:  # recursive call on left and right halves
                i_left, left_error, left_val_dict, left_lines = _ad_quad(function,
                                                                         a_1,
                                                                         (a_1 + b_1) / 2,
                                                                         tol_1 / 2,
                                                                         method_1,
                                                                         line_sum,
                                                                         val_dict)
                i_right, right_error, right_val_dict, right_lines = _ad_quad(function,
                                                                             (a_1 + b_1) / 2,
                                                                             b_1, tol_1 / 2,
                                                                             method_1,
                                                                             line_sum,
                                                                             val_dict)

            z_dict = left_val_dict
            z_dict.update(right_val_dict)

            return i_left + i_right, left_error + right_error, z_dict, left_lines + right_lines

            # merge dict: {**left_val_dict, **right_val_dict} can be used
            #    in certain newer versions of python
            # returns: sum of left and right approximations
            # sum of left and right error
            # merged left and right val_dicts
            # and the sum of the lines run

        elif method_1 == 'SIMPSON_38':  # Simpson's 3/8 rule
            # http://mathfaculty.fullerton.edu/mathews/n2003/Simpson38RuleMod.html

            h1 = (b_1 - a_1) / 3  # interval size for approx i_one
            h2 = (b_1 - a_1) / 6  # interval size for approx i_two
            x_1 = a_1 + h2
            x_2 = x_1 + h2
            x_3 = x_2 + h2
            x_4 = x_3 + h2
            x_5 = x_4 + h2

            if x_1 in val_dict:
                fx_1 = val_dict[x_1]
            else:
                fx_1 = function(x_1)
                val_dict[x_1] = fx_1
            if x_2 in val_dict:
                fx_2 = val_dict[x_2]
            else:
                fx_2 = function(x_2)
                val_dict[x_2] = fx_2
            if x_3 in val_dict:
                fx_3 = val_dict[x_3]
            else:
                fx_3 = function(x_3)
                val_dict[x_3] = fx_3
            if x_4 in val_dict:
                fx_4 = val_dict[x_4]
            else:
                fx_4 = function(x_4)
                val_dict[x_4] = fx_4
            if x_5 in val_dict:
                fx_5 = val_dict[x_5]
            else:
                fx_5 = function(x_5)
                val_dict[x_5] = fx_5

            i_one = (3*h1 / 8) * (fa + (3 * fx_2) + (3 * fx_4) + fb)
            i_two = (3*h2 / 8) * (fa + (3 * fx_1) + (3 * fx_2) + (3 * fx_3)
                                  + (3 * fx_4) + (3 * fx_5) + fb)
            max_error = np.abs(i_two - i_one) / 15  # calculates upper bound on error
                                                    # for Simpson's 3/8 composite

            if max_error < tol_1:
                return i_two, max_error, val_dict, line_sum
            else:  # recursive call on left and right halves
                i_left, left_error, left_val_dict, left_lines = _ad_quad(function,
                                                                         a_1,
                                                                         (a_1 + b_1) / 2,
                                                                         tol_1 / 2,
                                                                         method_1,
                                                                         line_sum,
                                                                         val_dict)
                i_right, right_error, right_val_dict, right_lines = _ad_quad(function,
                                                                             (a_1 + b_1) / 2,
                                                                             b_1, tol_1 / 2,
                                                                             method_1,
                                                                             line_sum,
                                                                             val_dict)

            z_dict = left_val_dict
            z_dict.update(right_val_dict)

            return i_left + i_right, left_error + right_error, z_dict, left_lines + right_lines

            # merge dict: {**left_val_dict, **right_val_dict} can be used in certain
            #    newer versions of python
            # returns: sum of left and right approximations
            # sum of left and right error
            # merged left and right val_dicts
            # and the sum of the lines run

        else:  # other condition performs TRAPEZOIDAL RULE
            h1 = b_1 - a_1  # interval size for approx i_one
            h2 = (b_1 - a_1) / 2  # interval size for approx i_two

            i_one = (h1 / 2) * (fa + fb)
            i_two = (h2 / 2) * (fa + (2 * fm) + fb)
            max_error = np.abs(i_two - i_one) / 3  # calculates upper bound on error for trap

            if max_error < tol_1:
                return i_two, max_error, val_dict, line_sum
            else:  # recursive call on left and right halves
                i_left, left_error, left_val_dict, left_lines = _ad_quad(function,
                                                                         a_1,
                                                                         (a_1 + b_1) / 2,
                                                                         tol_1 / 2,
                                                                         method_1,
                                                                         line_sum,
                                                                         val_dict)
                i_right, right_error, right_val_dict, right_lines = _ad_quad(function,
                                                                             (a_1 + b_1) / 2,
                                                                             b_1, tol_1 / 2,
                                                                             method_1,
                                                                             line_sum,
                                                                             val_dict)

            z_dict = left_val_dict
            z_dict.update(right_val_dict)

            return i_left + i_right, left_error + right_error, z_dict, left_lines + right_lines

            # merge dict: {**left_val_dict, **right_val_dict} can be used in certain
            #   newer versions of python
            # returns: sum of left and right approximations
            # sum of left and right error
            # merged left and right val_dicts
            # and the sum of the lines run

    def _std_quad(function, a_1, b_1, tol_1, method_1, total_lines_1, double_nodes_1=True):
        """
            Approximate the integral of function func, on the interval [a,b]
            return the approximation and an upper bound on the error.

            Called from quad. This function uses the standard quadrature method.
            _st_quad is defined from within a_quad because it should be only be
            called from within quad but must remain separate for multiple calls.

            Args:
                function: the function to be integrated
                a_1 (float): the lower bound of the interval of integration
                b_1 (float): the upper bound of the interval of integration
                tol_1 (float): desired error tolerance, defaults to 1e-6
                method_1 (str): quadrature method to be used, defaults to 'TRAP'
                total_lines_1 (int): the total number of lines run
                double_nodes_1 (bool, optional): True doubles the amount of nodes at each step,
                    defaults to True


            Returns:
                Integral Approximation (float): The Approximation of the integral
                Error upper bound (float): An upper bound on the error of the approximation
                Nodes dictionary (dict): A dictionary of the points used to
                    approximate the integral
                Total lines run (int): The total number of lines run by the function
        """

        line_sum = total_lines_1

        # interval validity
        if a_1 > b_1:
            a_1, b_1 = b_1, a_1

        if method_1 == 'SIMPSON':
            # calculates based on the composite Simpson's rule
            n = 4
            h2 = (b_1 - a_1) / n
            h1 = h2 * 2
            x_0, x_1, x_2, x_3, x_4 = a_1, a_1 + h2, a_1 + h1, a_1 + 3*h2, b_1
            y_0, y_1, y_2, y_3, y_4 = function(x_0), function(x_1), function(x_2),\
                                      function(x_3), function(x_4)

            val_dict = {x_0: y_0, x_1: y_1, x_2: y_2, x_3: y_3, x_4: y_4}

            sum_1 = (y_0 + 4 * y_2 + y_4)
            sum_2 = (y_0 + (4 * y_1) + (2 * y_2) + (4 * y_3) + y_4)

            i_one = (h1 / 3) * sum_1
            i_two = (h2 / 3) * sum_2

            while np.abs(i_two - i_one) > 15 * tol_1:
                if double_nodes:
                    n *= 2  # vs += 2 which only adds 2 (minimal nodes)
                else:       # but does not calc accurately
                    n += 2
                h2 = (b_1 - a_1) / n
                i_one = i_two
                sum_2 = val_dict[a_1] + val_dict[b_1]
                for i in range(1, n):
                    x_val = a_1 + i*h2
                    if x_val in val_dict:
                        y_val = val_dict[x_val]
                    else:
                        y_val = function(x_val)
                        val_dict[x_val] = y_val
                    if i % 2 == 1:  # MADE A CHANGE HERE TO CORRECT ISSUE
                        sum_2 += 4 * y_val
                    else:
                        sum_2 += 2 * y_val
                i_two = (h2 / 3) * sum_2
            return i_two, np.abs(i_two - i_one)/15, val_dict, line_sum

        elif method_1 == "SIMPSON_38":
            # calculates based on the  Simpson's 3/8 rule

            n = 6
            h2 = (b_1 - a_1) / n
            h1 = h2 * 2
            x_0, x_1, x_2, x_3, x_4, x_5, x_6 = a_1, a_1 + h2, a_1 + 2*h2,\
                                                a_1 + 3 * h2, a_1 + 4*h2, a_1 + 5*h2, b_1
            y_0, y_1, y_2, y_3, y_4, y_5, y_6 = function(x_0), function(x_1),\
                                                function(x_2), function(x_3),\
                                                function(x_4), function(x_5), function(x_6)

            val_dict = {x_0: y_0, x_1: y_1, x_2: y_2, x_3: y_3,
                        x_4: y_4, x_5: y_5, x_6: y_6}

            sum_1 = (y_0 + 3*y_2 + 3*y_4 + y_6)
            sum_2 = sum_1 + 3*y_1 + 3*y_3 + 3*y_5

            i_one = (3*h1 / 8) * sum_1  # 3/8 multiplier
            i_two = (3*h2 / 8) * sum_2

            while np.abs(i_two - i_one) > 15 * tol_1:
                if double_nodes_1:
                    n *= 2   # vs += 3 which only adds 3 (minimal nodes)
                else:        # but does not calc accurately
                    n += 3
                h2 = (b_1 - a_1) / n
                i_one = i_two
                sum_2 = val_dict[a_1] + val_dict[b_1]
                for i in range(1, n):
                    x_val = a_1 + i * h2
                    if x_val in val_dict:
                        y_val = val_dict[x_val]
                    else:
                        y_val = function(x_val)
                        val_dict[x_val] = y_val
                    sum_2 += 3*y_val
                i_two = (3*h2 / 8) * sum_2  # 3/8 multiplier
            return i_two, np.abs(i_two - i_one)/15, val_dict, line_sum
        else:
            # calculates based on the trapezoidal rule

            n = 2
            h2 = (b_1 - a_1) / n
            h1 = h2 * 2
            x_0, x_1, x_2 = a_1, a_1 + h2, b_1
            y_0, y_1, y_2 = function(x_0), function(x_1), function(x_2)

            val_dict = {x_0: y_0, x_1: y_1, x_2: y_2}

            sum_1 = (y_0 + y_2)
            sum_2 = sum_1 + 2 * y_1

            i_one = (h1 / 2) * sum_1
            i_two = (h2/ 2) * sum_2

            while np.abs(i_two - i_one) > 3 * tol_1:
                if double_nodes:
                    n *= 2  # vs += 1 which only adds 1 (minimal nodes)
                else:       # but does not calc accurately
                    n += 1
                h2 = (b_1 - a_1) / n
                i_one = i_two
                sum_2 = val_dict[a_1] + val_dict[b_1]
                for i in range(1, n):
                    x_val = a_1 + i * h2
                    if x_val in val_dict:
                        y_val = val_dict[x_val]
                    else:
                        y_val = function(x_val)
                        val_dict[x_val] = y_val
                    sum_2 += 2 * y_val
                i_two = (h2 / 2) * sum_2
            return i_two, np.abs(i_two - i_one)/3, val_dict, line_sum

    if adaptive:
        packed_data = _ad_quad(func, a, b, tol, method, total_lines_1=0, val_dict_1={})
    else:
        packed_data = _std_quad(func, a, b, tol, method, total_lines_1=0,
                                double_nodes_1=double_nodes)

    if visual_mode:
        method_dict = {"TRAP": "composite trapezoidal", "SIMPSON": "composite Simpson's",
                       "SIMPSON_38": "composite Simpson's 3/8"}  # used for formatting of the plots

        points_dict = packed_data[2]
        x_values = np.array(list(points_dict.keys()))
        y_values = np.array(list(points_dict.values()))
        y_max = np.max(y_values)
        y_min = np.min(y_values)

        plt.plot(x_values, y_values, "ro", label="Nodes")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.ylim(y_min - (y_max - y_min) / 12, y_max + (y_max - y_min) / 12)
        plt.xlim(a - (b - a) / 12, b + (b - a) / 12)
        plt.title("Nodes used in integral approximation with %s %s method"
                  % ("adaptive" if adaptive else "standard", method_dict[method]))

        plt.suptitle("Approximation: %s, Error upper bound: %s, total nodes: %s"
                     % (packed_data[0], packed_data[1], len(packed_data[2])))

        plt.legend()
        plt.show()

    return packed_data[:3]


def quad_comparison(func, a, b, num_tests=11, visual_mode=True):
    """
        Compares the error vs number of nodes used for 4 integration techniques.

        Compares the adaptive and non-adaptive trapezoidal and Simpson's rules
        by running tests with difference error tolerances and recording the
        number of nodes used to achieve a given error bound

        Args:
            func: the function to be integrated
            a (float): the lower bound of the interval of integration
            b (float): the upper bound of the interval of integration
            num_tests (int): The number of tests to be performed, defaults to 11
            visual_mode (bool): Activates/deactivates graph mode, defaults to True


        Returns:
            node_data (pandas DataFrame): Node data produced by tests
            Error (pandas DataFrame): Error data produced by tests
            """
    num_methods = 4
    node_methods = ['Adaptive TRAP', 'Adaptive SIMPSON', 'Standard TRAP', 'Standard SIMPSON']
    error_methods = ['Adaptive TRAP', 'Adaptive SIMPSON', 'Standard TRAP', 'Standard SIMPSON']
    errors = np.array([10.0 / (5 ** i) for i in range(num_tests)])
    node_data = DataFrame(np.ones([num_tests, num_methods]),
                          index=errors, columns=node_methods)
    error_data = DataFrame(np.ones([num_tests, num_methods]),
                           index=errors, columns=error_methods)

    for i in range(num_methods):
        for j in range(num_tests):
            if node_methods[i].split()[0] == 'Adaptive':
                p_data = quad(func, a, b, tol=errors[j],
                              method=node_methods[i].split()[1],
                              adaptive=True)
                nodes = len(p_data[2])
                err = p_data[1]
                node_data.iloc[j, i] = nodes
                error_data.iloc[j, i] = err
            elif node_methods[i].split()[0] == 'Standard':
                if node_methods[i].split()[1] == 'SIMPSON':
                    p_data = quad(func, a, b, tol=errors[j],
                                  method=node_methods[i].split()[1],
                                  double_nodes=True,
                                  adaptive=False)
                else:
                    p_data = quad(func, a, b, tol=errors[j],
                                  method=node_methods[i].split()[1],
                                  adaptive=False)
                nodes = len(p_data[2])
                err = p_data[1]
                node_data.iloc[j, i] = nodes
                error_data.iloc[j, i] = err


            # print(data.iloc[j, i * 2])

    if visual_mode:
        fig = plt.figure(figsize=(10, 6))
        plt.plot(error_data, node_data)
        plt.xscale('log')
        plt.yscale('log')
        plt.gca().invert_xaxis()
        plt.legend(node_data.columns, loc=2, prop={'size': 10})
        plt.xlabel('Upper Bound on Error')
        plt.ylabel('Number of Nodes Used')
        plt.title('A Comparison Of Methods')

        plt.show()
    # print(node_data)

    return node_data, error_data

if __name__ == "__main__":

    # print(len(quad(lambda x: np.sin(2 * x) * x, -2, 13, tol=1e-5,
    #                method="SIMPSON", adaptive=True, visual_mode=False)[2]))
    # print(len(quad(lambda x: np.sin(2 * x) * x, -2, 13, tol=1e-8,
    #                method="SIMPSON", adaptive=True, visual_mode=False)[2]))
    # quad_comparison(lambda x: np.sin(2*x)*x, -1, 3, num_tests=11)
    # quad_comparison(lambda x: np.exp(np.power(x, 2)), -3, 1, num_tests=6,
    #                 visual_mode=True)
    # quad(lambda x: np.exp(np.power(x, 2)), -3, 1, method='SIMPSON', visual_mode=True)
    quad(lambda x: x * np.sin(2 * np.log(x)), 1, 18, tol=1e-4, method='TRAP', adaptive=False,
         double_nodes=True, visual_mode=True),
