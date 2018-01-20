import os
from .ExpressionEvaluator import ExpressionEvaluator

# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

class VariableNotFoundError(Exception):
    """Variable not found error."""

class RequiredPathNotFoundError(Exception):
    """Required path not found error."""

class Template(object):
    """
    Creates a template object based on a string defined using template syntax.

    A template string is a compound of variables that were collected by the
    crawler and passed for the running:
        '{prefix}/testing/{width}X{height}/{name}.(pad {frame} 10).{ext}'

    The template string can contain the prefix "!" which is used to tell
    that the level must exist, for instance:
        '{prefix}/!shouldExist/{width}X{height}/{name}.(pad {frame} 10).{ext}'

    Also, you can use the token "<parentPath>" to pass the computed parent path
    to an expression. Keep in mind this is only supported by expressions.
        '{prefix}/testing/(computeVersion <parentPath>)/{name}.(pad {frame} 10).{ext}'
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

    def valueFromCrawler(self, crawler, vars={}):
        """
        Return the value of the template based on a crawler.
        """
        contextVariableValues = {}
        for varName in self.varNames():
            if varName in vars:
                contextVariableValues[varName] = str(vars[varName])
            else:
                contextVariableValues[varName] = str(crawler.var(varName))

        return self.value(contextVariableValues)

    def value(self, vars={}):
        """
        Return the value of the template based on the input variables.
        """
        self.__validateTemplateVariables(vars)

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
                # Potentially we could add support for "<expression>" rather
                # than "(expression)" to tell to avoid this cache. However, the
                # default behaviour should be to always cache it (never change it)
                # otherwise it could side effect in expressions that create
                # new versions...
                rawExpression = templatePart[:endIndex]

                # this is a special token that allows to pass the parent path
                # to an expression, replacing it with the parent path at this point.
                rawExpression = rawExpression.replace("<parentPath>", finalResolvedTemplate.replace("!", ""))
                if rawExpression not in self.__expressionValueCache:
                    self.__expressionValueCache[rawExpression] = ExpressionEvaluator.parseRun(
                        rawExpression
                    )

                expressionValue = self.__expressionValueCache[rawExpression]
                finalResolvedTemplate += expressionValue + templatePart[endIndex + 1:]
            else:
                finalResolvedTemplate += templatePart

        # resolving required path levels
        if "!" in finalResolvedTemplate:
            finalPath = []
            for pathLevel in finalResolvedTemplate.split(os.sep):
                if pathLevel.startswith("!"):
                    finalPath.append(pathLevel[1:])
                    resolvedPath = os.sep.join(finalPath)
                    if not os.path.exists(resolvedPath):
                        raise RequiredPathNotFoundError(
                            'Template contains a path marked as required:\n"{0}"\n\nThis error is caused because the target path does not exist in the file system:\n{1}'.format(
                                pathLevel,
                                resolvedPath
                            )
                        )

                else:
                    finalPath.append(pathLevel)
            finalResolvedTemplate = os.sep.join(finalPath)

        return finalResolvedTemplate

    def __validateTemplateVariables(self, vars):
        """
        Make sure the variables used by template are available, otherwise thown an exception (VariableNotFoundError).
        """
        for requiredVarName in self.varNames():
            if requiredVarName not in vars:
                raise VariableNotFoundError(
                    'Could not find a value for the variable {0}'.format(
                        requiredVarName
                    )
                )

    def __setVarNames(self):
        """
        Set the variable names found in the input template.
        """
        result = set()

        # detecting variables
        for templatePart in self.inputString().split("{"):
            if templatePart is '' or "}" not in templatePart:
                continue

            endIndex = templatePart.find('}')
            result.add(templatePart[:endIndex])

        self.__varNames = list(result)

    def __setRawTemplateString(self, inputString):
        """
        Set the raw template string.
        """
        assert isinstance(inputString, basestring), \
            "Invalid template string!"

        self.__inputString = inputString
