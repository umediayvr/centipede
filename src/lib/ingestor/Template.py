import os
from .ExpressionEvaluator import ExpressionEvaluator

class VariableNotFoundError(Exception):
    """Variable not found error."""

class Template(object):
    """
    Creates a template object based on a string defined using template syntax.

    A template string is a compound of variables that were collected by the
    crawler and passed for the running:
        '{prefix}/testing/{width}X{height}/{name}.(pad {frame} 10).{ext}'
    """

    def __init__(self, inputString):
        """
        Create a template object.
        """
        self.__setRawTemplateString(inputString)
        self.__setVarNames()
        self.__expressionValueCache = {}

    def inputString(self):
        """
        Return the raw template string used to create the object.
        """
        return self.__inputString

    def varNames(self):
        """
        Return a list of variable names found in the input string.
        """
        return self.__varNames

    def value(self, vars={}):
        """
        Return the value of the template based on the input variables.
        """
        # validating values for the template variables
        for requiredVarName in self.varNames():
            if requiredVarName not in vars:
                raise VariableNotFoundError(
                    'Could not find a value for the variable {0}'.format(
                        requiredVarName
                    )
                )

        # resolving variables values
        resolvedTemplate = self.inputString()
        for varName, varValue in vars.items():
            resolvedTemplate = resolvedTemplate.replace(
                ('{' + varName + '}'),
                str(varValue)
            )

        # resolving function values
        finalResolvedTemplate = ""
        for templatePart in resolvedTemplate.split("("):

            endIndex = templatePart.find(')')
            if endIndex != -1:

                # processing the expression only when it has not been
                # evaluated yet, otherwise return it from the cache.
                # Potentially we could add support for the prefix "!expression"
                # to tell to avoid this cache. However, the behaviour default
                # should be to always cache it (never change it) otherwise
                # it could side effect in expressions that create a new version
                # for instance...
                rawExpression = templatePart[:endIndex]
                if rawExpression not in self.__expressionValueCache:
                    self.__expressionValueCache[rawExpression] = ExpressionEvaluator.parseRun(
                        rawExpression
                    )

                expressionValue = self.__expressionValueCache[rawExpression]
                finalResolvedTemplate += expressionValue + templatePart[endIndex+1:]
            else:
                finalResolvedTemplate += templatePart

        return finalResolvedTemplate

    def __setVarNames(self):
        """
        Set the variable names found in the input template.
        """
        result = set()

        # detecting variables
        for templatePart in self.inputString().split("{"):
            if templatePart is '':
                continue

            endIndex = templatePart.find('}')
            result.add(templatePart[:endIndex])

        self.__varNames = list(result)

    def __setRawTemplateString(self, inputString):
        """
        Set the raw template string.
        """
        assert isinstance(inputString, str), \
            "Invalid template string!"

        self.__inputString = inputString
