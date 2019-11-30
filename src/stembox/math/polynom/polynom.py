"""Representing and solving problems with polynomials."""
from typing import List, Dict
from ..expression import Expression
from copy import deepcopy
from ...stembox import Solution, Step, Explanation, ListIllustration
from ..factor import Factor, Variable, Power, Fraction, Number
from ..equation import Equation
from ..logic import Equivalence
from . import explans as xpl


class Monomial(Expression):
    def __init__(self, factors: List[Factor], **kwargs):
        super().__init__(**kwargs)
        self.factors = factors


class Polynomial(Expression):
    def __init__(self, terms: List[Monomial], **kwargs):
        super().__init__(**kwargs)
        self.terms = terms


def _get_var_paths(monomial: Monomial) -> List[str]:
    vars = []
    for i, f in enumerate(monomial.factors):
        path = '$.factors'
        if isinstance(f, Variable):
            path += f'[{i}]'
        elif isinstance(f, Power) and isinstance(f.base, Variable):
            path += f'[{i}].base'
        elif isinstance(f, Fraction) and isinstance(f.numerator, Variable):
            path += f'[{i}].numerator'
        else:
            continue
        vars.append(path)
    return vars


def _get_vars(monomial: Monomial) -> List[Variable]:
    return [monomial.get_at_path(path)
            for path in _get_var_paths(monomial)]


def _get_no_expon_var_paths(monomial: Monomial) -> List[str]:
    """Return the paths of the variables that lack an exponent."""
    return [p for p in _get_var_paths(monomial)
            if not p.endswith('.base')]


def _get_no_expon_vars(monomial: Monomial) -> List[Variable]:
    """Return the variables that lack an exponent."""
    return [monomial.get_at_path(path)
            for path in _get_no_expon_var_paths(monomial)]


def solve_find_vars(monomial: Monomial) -> Solution:
    """Return the solution for finding the variables in the given monomial.
    """
    # PURPOSE
    purpose = Explanation(description=xpl.SEARCH_MONOM_VARS_PURPOSE_DESCR())

    # EXECUTION
    var_paths = _get_var_paths(monomial)
    monom_exe = deepcopy(monomial)

    for i, var_path in enumerate(var_paths):
        var = monom_exe.get_at_path(var_path)
        var.label = xpl.SEARCH_MONOM_VARS_EXEC_LABEL(i + 1)
        var.mark = i

    execution = Explanation(illustration=monom_exe)

    # RESULT
    monom_res = deepcopy(monom_exe)
    for var_path in var_paths:
        var = monom_res.get_at_path(var_path)
        var.label = None

    result = Explanation(
        description=xpl.SEARCH_MONOM_VARS_RESULT_DESCR(var_paths),
        illustration=monom_res)

    return Solution(steps=[Step(purpose=purpose,
                                execution=execution,
                                result=result)],
                    value=var_paths)


def solve_unit_var_exponent(monomial: Monomial,
                            var_paths: List[str]) -> Solution:
    """
    Return the solution for explicitely adding a unit exponent to all
    variables that do not have an exponent.

    The `value` property of the returned `Solution` will contain the monomial
    version with all explicit variable exponents.

    Args:
        monomial (Monomial): the monomial to add unit exponents to the
        variables
        var_paths (List[str]): the illustration paths of the variables that
        should obtain an explicit exponent
    """
    no_expon_vars = ({*_get_no_expon_var_paths(monomial)}
                     .intersection({*var_paths}))

    if len(no_expon_vars) == 0:
        # All variables have an exponent, so return a Solution without any
        # steps
        return Solution(value=deepcopy(monomial))

    # PURPOSE
    purpose = Explanation(
        description=xpl.UNIT_VAR_EXPONENT_PURPOSE_DESCR()
    )

    # EXECUTION
    for i, var in enumerate(no_expon_vars):
        var.mark = i

    # Copy the monomial and, in the old monomial, label the variables that
    # do not have an exponent
    old_monom = deepcopy(monomial)
    for i, p in enumerate(_get_no_expon_var_paths(old_monom)):
        var = old_monom.get_at_path(p)
        var.label = xpl.UNIT_VAR_EXPONENT_EXEC_LABEL()

    # In the new monomial, wrap Powers around variables
    new_monomial = deepcopy(monomial)
    for i, p in enumerate(_get_no_expon_var_paths(new_monomial)):
        var = new_monomial.get_at_path(p)
        new_monomial.set_at_path(p, Power(base=var, exponent=Number(1)))

    execution = Explanation(
        description=xpl.UNIT_VAR_EXPONENT_EXEC_DESCR(),
        illustration=Equivalence([old_monom, deepcopy(new_monomial)])
    )

    # RESULT
    result = Explanation(
        decription=xpl.UNIT_VAR_EXPONENT_RESULT_DESCR(),
        illustration=deepcopy(new_monomial))

    return Solution(steps=[Step(purpose=purpose, execution=execution,
                                result=result)],
                    value=deepcopy(new_monomial))


def solve_find_var_expons(monomial: Monomial,
                          var_paths: List[str]) -> Solution:
    """Return the solution for finding the exponents of each variable.

    The solution value will contain a dict with the illustration paths of the
    variables as key and the illustration path of the corresponding exponents
    as value.

    Args:
        monomial (Monomial): the monomial in which to search for the variable
        exponents
        var_paths (List[str]): a list of paths that contain the variables
    """
    # 1. Write 1 as exponent of variables with no exponent
    solution = solve_unit_var_exponent(monomial, var_paths)

    # All var_paths should now end with `.base`, as they are all wrapped inside
    # a `Power` now
    var_paths = [p if p.endswith('.base') else p + '.base'
                 for p in var_paths]

    # 2. Mark the exponents
    if len(solution) > 0:
        monomial = deepcopy(solution.value)

    # PURPOSE
    purpose = Explanation(
        description=xpl.SEARCH_VAR_EXPON_PURPOSE_DESCR(len(var_paths)))

    # EXECUTION
    var_expons = {}
    monom_exe = deepcopy(monomial)
    for i, var_path in enumerate(var_paths):
        if var_path.endswith('.base'):
            pow_path = var_path[:var_path.rfind('.base')]
            power = eval(f'monomial{pow_path[1:]}')
            power.exponent.mark = power.base.mark
            power.exponent.label = xpl.SEARCH_VAR_EXPON_EXEC_LABEL(
                var_path)
            var_expons[var_path] = pow_path + '.exponent'
    execution = Explanation(illustration=monom_exe)

    # RESULT
    result = Explanation(
        description=xpl.SEARCH_VAR_EXPON_RESULT_DESCR(var_expons),
        illustration=deepcopy(monom_exe))

    solution.append(Step(purpose=purpose,
                         execution=execution,
                         result=result))
    solution.value = var_expons
    return solution


def solve_add_exponents(monomial: Monomial,
                        var_expons: Dict[str, str]) -> Solution:
    """Return the solution for adding the given exponents

    The value of the returned `Solution` will be the sum of the exponents,
    represented as a `Number` object.
    """
    # PURPOSE
    purpose = Explanation(description=xpl.ADD_EXPONENTS_PURPOSE_DESCR())

    # EXECUTION
    monom_exec = deepcopy(monomial)
    expons = [monom_exec.get_at_path(p) for _, p in var_expons.items()]

    # Make a list of illustrations, where the first element contains the
    # original monomial and the second element shows the addition. That way, we
    # can still refer to the variables, which is necessary to explain for each
    # of the exponents to which variable they originally belonged.
    var_paths = [f'$[0]{var_path[1:]}' for var_path in var_expons.keys()]
    for var_path, expon in zip(var_paths, expons):
        expon.label = xpl.ADD_EXPONENTS_EXEC_ILLUSTR_LABEL(var_path)

    exp_sum = Number(sum(exp.value for exp in expons))
    eqn = Equation(lhs=Polynomial([Monomial([exp]) for exp in expons]),
                   rhs=exp_sum)
    execution = Explanation(illustration=ListIllustration([monom_exec, eqn]),
                            description=xpl.ADD_EXPONENTS_EXEC_DESCR('$[1]'))

    # RESULT
    return Solution(steps=[Step(purpose, execution)],
                    value=exp_sum)


def solve_find_grade(monomial: Monomial) -> Solution:
    # PURPOSE
    purpose = Explanation(description=xpl.FIND_MONOMIAL_GRADE_PURPOSE_DESCR())

    # EXECUTION
    # Find variables
    vars_solution = solve_find_vars(monomial)

    # Find exponents of variables
    var_paths = vars_solution.value
    expon_solution = solve_find_var_expons(monomial, var_paths)

    # Sum exponents
    var_expons = expon_solution.value
    sum_solution = solve_add_exponents(monomial, var_expons)
    monom_grade = sum_solution.value

    execution = Solution(steps=[*vars_solution,
                                *expon_solution,
                                *sum_solution],
                         value=monom_grade)

    # RESULT
    result = Explanation(
        description=xpl.FIND_MONOMIAL_GRADE_RESULT_DESCR('$'),
        illustration=monom_grade)

    return Solution([Step(purpose, execution, result)],
                    value=monom_grade)
