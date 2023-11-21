from nltk.inference.resolution import ResolutionProver, ResolutionProverCommand
from nltk.sem.logic import (AllExpression, AndExpression,
                            ApplicationExpression, EqualityExpression,
                            ExistsExpression, IffExpression, ImpExpression,
                            IndividualVariableExpression, NegatedExpression,
                            OrExpression, Variable, VariableExpression,
                            skolem_function, unique_variable)
from nltk.sem.skolemize import skolemize, to_cnf

print('Loading patch')

def _skolemize(expression, univ_scope=None, used_variables=None):
    """
    Skolemize the exp
    """
    # print('My skolemize')
    if univ_scope is None:
        univ_scope = set()
    if used_variables is None:
        used_variables = set()

    if isinstance(expression, AllExpression):
        term = skolemize(
            expression.term,
            univ_scope | {expression.variable},
            used_variables | {expression.variable},
        )
        return term.replace(
            expression.variable,
            VariableExpression(unique_variable(ignore=used_variables)),
        )
    elif isinstance(expression, AndExpression):
        return skolemize(expression.first, univ_scope, used_variables) & skolemize(
            expression.second, univ_scope, used_variables
        )
    elif isinstance(expression, OrExpression):
        return to_cnf(
            skolemize(expression.first, univ_scope, used_variables),
            skolemize(expression.second, univ_scope, used_variables),
        )
    elif isinstance(expression, ImpExpression):
        return to_cnf(
            skolemize(-expression.first, univ_scope, used_variables),
            skolemize(expression.second, univ_scope, used_variables),
        )
    elif isinstance(expression, IffExpression):
        return to_cnf(
            skolemize(-expression.first, univ_scope, used_variables),
            skolemize(expression.second, univ_scope, used_variables),
        ) & to_cnf(
            skolemize(expression.first, univ_scope, used_variables),
            skolemize(-expression.second, univ_scope, used_variables),
        )
    elif isinstance(expression, EqualityExpression):
        return expression
    elif isinstance(expression, NegatedExpression):
        negated = expression.term
        if isinstance(negated, AllExpression):
            term = skolemize(
                -negated.term, univ_scope, used_variables | {negated.variable}
            )
            # if univ_scope:
            return term.replace(negated.variable, skolem_function(univ_scope))
            # else:
            #     skolem_constant = VariableExpression(
            #         unique_variable(ignore=used_variables)
            #     )
            #     return term.replace(negated.variable, skolem_constant)
        elif isinstance(negated, AndExpression):
            return to_cnf(
                skolemize(-negated.first, univ_scope, used_variables),
                skolemize(-negated.second, univ_scope, used_variables),
            )
        elif isinstance(negated, OrExpression):
            return skolemize(-negated.first, univ_scope, used_variables) & skolemize(
                -negated.second, univ_scope, used_variables
            )
        elif isinstance(negated, ImpExpression):
            return skolemize(negated.first, univ_scope, used_variables) & skolemize(
                -negated.second, univ_scope, used_variables
            )
        elif isinstance(negated, IffExpression):
            return to_cnf(
                skolemize(-negated.first, univ_scope, used_variables),
                skolemize(-negated.second, univ_scope, used_variables),
            ) & to_cnf(
                skolemize(negated.first, univ_scope, used_variables),
                skolemize(negated.second, univ_scope, used_variables),
            )
        elif isinstance(negated, EqualityExpression):
            return expression
        elif isinstance(negated, NegatedExpression):
            return skolemize(negated.term, univ_scope, used_variables)
        elif isinstance(negated, ExistsExpression):
            term = skolemize(
                -negated.term,
                univ_scope | {negated.variable},
                used_variables | {negated.variable},
            )
            return term.replace(
                negated.variable,
                VariableExpression(unique_variable(ignore=used_variables)),
            )
        elif isinstance(negated, ApplicationExpression):
            return expression
        else:
            return expression
            raise Exception("'%s' cannot be skolemized" % expression)
    elif isinstance(expression, ExistsExpression):
        term = skolemize(
            expression.term, univ_scope, used_variables | {expression.variable}
        )
        # if univ_scope:
        return term.replace(expression.variable, skolem_function(univ_scope))
        # else:
        #     skolem_constant = VariableExpression(unique_variable(ignore=used_variables))
        #     return term.replace(expression.variable, skolem_constant)
    elif isinstance(expression, ApplicationExpression):
        return expression
    else:
        return expression
        raise Exception("'%s' cannot be skolemized" % expression)
    
def _find_answers(self, verbose=False):
        # print("My find answers")
        self.prove(verbose)
        answers = set()
        answer_ex = VariableExpression(Variable(ResolutionProver.ANSWER_KEY))
        for clause in self._clauses:
           if (len(clause) == 1
                and isinstance(clause[0], ApplicationExpression)
                and clause[0].function == answer_ex
                and not isinstance(clause[0].argument, IndividualVariableExpression)
            ):
                answers.add(clause[0].argument)
        return answers

def patch():
    print("Patching nltk.sem.logic")
    # nltk.inference.resolution.ResolutionProverCommand.find_answers = _find_answers
    # setattr(nltk.inference.resolution.ResolutionProverCommand, 'find_answers', _find_answers)
    ResolutionProverCommand.find_answers.__code__ = _find_answers.__code__
    # Monkey patch skolemize function in nltk.sem.skolemize by skolemize function
    # print(type(nltk.sem.skolemize.skolemize))
    skolemize.__code__ = _skolemize.__code__
    # setattr(nltk.sem.skolemize, 'skolemize', _skolemize)
    # skolemize = _skolemize

patch()