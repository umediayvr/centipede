import os
import uuid
from .Procedure import Procedure

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

    A template string can contain variables using the syntax {crawlerVariable},
    procedures using the syntax (myprocedure). Procedures can receive
    arguments for instance (myprocedure {crawlerVariable}) where the arguments must
    be separated by space like in bash.
        '/tmp/{myVariable}/(myprocedure {myVariable})'

    Also, template engine provides special tokens designed to help with
    path manipulation:

    /! - Means the directory must exist for instance:
        '{prefix}/!shouldExist/{width}X{height}/{name}.(pad {frame} 10).{ext}'

    <parent> - Passes the computed parent path to a procedure. Keep in mind this
    is only supported by procedures.
        '{prefix}/testing/(computeVersion <parent>)/{name}.(pad {frame} 10).{ext}'
    """

    __safeTokenId = uuid.uuid4()

    def __init__(self, inputString=""):
        """
        Create a template object.
        """
        self.setInputString(inputString)
        self.__setVarNames()
        self.__procedureValueCache = {}

    def inputString(self):
        """
        Return the raw template string used to create the object.
        """
        return self.__inputString

    def setInputString(self, inputString):
        """
        Set the template string.
        """
        assert isinstance(inputString, basestring), \
            "Invalid template string!"

        self.__inputString = inputString

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
                self.__escapeTemplateTokens(varValue)
            )

        # resolving function values
        finalResolvedTemplate = ""
        for templatePart in resolvedTemplate.split("("):

            endIndex = templatePart.find(')')
            if endIndex != -1:

                # processing the procedure only when it has not been
                # evaluated yet, otherwise return it from the cache.
                # Potentially we could add support for "((procedure))" rather
                # than "(procedure)" to tell to avoid this cache. However, the
                # default behaviour should be to always cache it (never change it)
                # otherwise it could side effect in procedures that create
                # new versions...
                rawProcedure = templatePart[:endIndex]

                # this is a special token that allows to pass the parent path
                # to a procedure, replacing it with the parent path at this point.
                rawProcedure = rawProcedure.replace(
                    "<parent>",
                    self.__escapeTemplateTokens(finalResolvedTemplate.replace("/!", "/"), 0)
                )

                if rawProcedure not in self.__procedureValueCache:
                    # replacing any reserved token from the result of the procedure
                    self.__procedureValueCache[rawProcedure] = self.__escapeTemplateTokens(
                        Procedure.parseRun(
                            rawProcedure
                        )
                    )

                procedureValue = self.__procedureValueCache[rawProcedure]
                finalResolvedTemplate += procedureValue + templatePart[endIndex + 1:]
            else:
                finalResolvedTemplate += templatePart

        # resolving required path levels
        if "/!" in finalResolvedTemplate:
            finalPath = []
            for pathLevel in self.__escapeTemplateTokens(finalResolvedTemplate, 0).split(os.sep):
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

        # restoring all the espaped tokens to the original value
        finalResolvedTemplate = self.__escapeTemplateTokens(finalResolvedTemplate, 0)

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

    @classmethod
    def __escapeTemplateTokens(cls, value, direction=1):
        """
        Escape special template tokens from the input string.
        """
        safeFunctionStart = '<{}>'.format(cls.__safeTokenId)
        safeFunctionEnd = '</{}>'.format(cls.__safeTokenId)
        safeLevelExist = '[{}]'.format(cls.__safeTokenId)
        safeParentPath = '[[{}]]'.format(cls.__safeTokenId)

        if direction:
            return str(value).replace(
                "(", safeFunctionStart
            ).replace(
                ")", safeFunctionEnd
            ).replace(
                "/!", safeLevelExist
            ).replace(
                "<parent>", safeParentPath
            )

        return str(value).replace(
            safeFunctionStart, "("
        ).replace(
            safeFunctionEnd, ")"
        ).replace(
            safeLevelExist, "/!"
        ).replace(
            safeParentPath, "<parent>"
        )
