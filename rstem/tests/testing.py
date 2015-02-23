import testing_log
import traceback
import importlib
from functools import wraps
import os
import sys

SEPARATOR= '\n' + '=' * 78

class TestFailureException(Exception): pass
class TestSkippedException(TestFailureException): pass
class TestCancelledException(TestFailureException): pass

def enum(*names):
    for i, name in enumerate(names):
        globals()[name] = i
    return names

ordered_test_types = enum(
    'AUTOMATIC_TEST',
    'MANUAL_OUTPUT_TEST',
    'MANUAL_INPUT_TEST',
    )

def test_type_short_name(test_type):
    test_type_mapping = {
        'AUTOMATIC_TEST' : 'AUTO',
        'MANUAL_OUTPUT_TEST' : 'OUT',
        'MANUAL_INPUT_TEST' : 'IN',
    }
    try:
        return test_type_mapping[test_type]
    except KeyError:
        return "ERR"

def automatic(func):
    @wraps(func)
    def wrapper():
        print(SEPARATOR)
        print('AUTOMATIC TEST: {0}'.format(func.__name__))
        try:
            passed = func()
            if passed:
                print('--> PASSED')
                exc = 0
            else:
                print('--> FAILED')
                exc = TestFailureException()
        except Exception as e:
            print('--> FAILED BY EXCEPTION')
            print(traceback.format_exc())
            exc = e
        testing_log.write(func, ordered_test_types[wrapper.test_type], exc)
    wrapper.test_type = AUTOMATIC_TEST
    return wrapper

def manual_output(func):
    @wraps(func)
    def wrapper():
        retry = True
        print(SEPARATOR)
        while retry:
            retry = False
            print('MANUAL OUTPUT TEST: {0}'.format(func.__name__))
            print('VERIFY THE FOLLOWING:')
            for line in func.__doc__.split('\n'):
                print('\t' + line)
            ret = input('Press Enter to start test (s to skip):').strip()
            if ret and ret[0].lower() == 's':
                exc = TestSkippedException()
            else:
                exc = 0
                try:
                    func()
                except Exception as e:
                    print('--> FAILED BY EXCEPTION')
                    print(traceback.format_exc())
                    exc = e
                    break
                chosen = False
                while not chosen:
                    ret = input('Check the output - pass, fail, or retry? [P/f/r]: ').strip()
                    choice = ret[0].lower() if ret else 'p'
                    chosen = True
                    if choice == 'p':
                        exc = 0
                    elif choice == 'f':
                        exc = TestFailureException()
                    elif choice == 'r':
                        retry = True
                        pass
                    else:
                        chosen = False
                        print('INVALID CHOICE!')
        testing_log.write(func, ordered_test_types[wrapper.test_type], exc)
    wrapper.test_type = MANUAL_OUTPUT_TEST
    return wrapper

def manual_input(func):
    @wraps(func)
    def wrapper():
        print(SEPARATOR)
        print('MANUAL INPUT TEST: {0}'.format(func.__name__))
        print('PROVIDE THE FOLLOWING INPUT:')
        for line in func.__doc__.split('\n'):
            print('\t' + line)
        print('NOTE: Ctrl-C during this test will cancel only this test')
        ret = input('Press Enter to start test (s to skip):').strip()
        if ret and ret[0].lower() == 's':
            exc = TestSkippedException()
        else:
            exc = 0
            try:
                passed = func()
                if not passed:
                    raise TestFailureException()
            except KeyboardInterrupt:
                exc = TestCancelledException()
            except Exception as e:
                exc = e
        testing_log.write(func, ordered_test_types[wrapper.test_type], exc)
    wrapper.test_type = MANUAL_INPUT_TEST
    return wrapper

if __name__ == '__main__':
    #
    # Usage: python -m testing user_test_type user_test_name
    #
    # where:
    #   user_test_type is [*|auto|help]-testname.  Anything after (and
    #   including) the dash is ignored, if it is given.  The important part is
    #   just the suffix:
    #       *       Run all tests
    #       auto    Run only automatic tests
    #       manu    Run only manual tests
    #       help    Show test's docstring
    #   user_test_name is the python test file to run (without the .py extension)
    #
    user_test_type = sys.argv[1]
    try:
        # Remove everything after dash
        dash_index = user_test_type.index('-')
        user_test_type = user_test_type[:dash_index]
    except ValueError:
        pass
    module_name = 'test_' + sys.argv[2]
    module = importlib.import_module(module_name)
    funcs = [getattr(module, func) for func in dir(module)]
    tests = [func for func in funcs if hasattr(func, 'test_type')]
    if user_test_type == 'auto':
        test_types = [AUTOMATIC_TEST]
    elif user_test_type == 'manu':
        test_types = [MANUAL_OUTPUT_TEST, MANUAL_INPUT_TEST]
    elif user_test_type == 'help':
        print('#' * 78)
        print()
        print(module.__doc__)
        print()
        print('#' * 78)
        sys.exit()
    else:
        test_types = set([test.test_type for test in tests])

    # For each test type, in the defined order, run the tests
    testing_log.create()
    try:
        for t, name in enumerate(ordered_test_types):
            if t in test_types:
                # Run all tests of the given type
                for test in tests:
                    if test.test_type == t:
                        test()
    except KeyboardInterrupt as e:
        testing_log.keyboard_interrupt()
    testing_log.close()

    print(SEPARATOR)
    testing_log.print_result_table()

    print(SEPARATOR)
    testing_log.print_summary()

