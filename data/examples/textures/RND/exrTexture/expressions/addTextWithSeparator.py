import ingestor

def addTextWithSeparator(text, sep='_'):
    """
    Return a text with a separator in case there is a text.
    """
    return '{0}{1}'.format(sep, text) if text else ''


# registering expression
ingestor.ExpressionEvaluator.register(
    'addTextWithSeparator',
    addTextWithSeparator
)
