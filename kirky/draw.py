from pyx import path, deco, text, color
from copy import copy


def DrawEdge(edge, canvas):
    head = copy(edge.head)
    tail = copy(edge.tail)
    reversed = False
    if tail[0] - head[0] > 0:
        reversed = True
    for i in range(0, len(head)):
        head[i] *= 4
        tail[i] *= 4
    weight = edge.weight
    if weight == 0:
        return
    string = '%s' % weight
    """
    numerator = weight.numerator
    #if numerator == 0:
    #    return
    denominator = weight.denominator
    string = '%s/%s' % (numerator, denominator)
    """
    if not reversed:
        if string and string[0] == '-':
            canvas.stroke(path.line(tail[0], tail[1], head[0], head[1]), [deco.earrow, deco.curvedtext(string, textattrs=[text.vshift.mathaxis, text.size.tiny], exclude=0.1), color.rgb.red])
        elif string and string[0] != '-':
            canvas.stroke(path.line(head[0], head[1], tail[0], tail[1]), [deco.barrow, deco.curvedtext(string, textattrs=[text.vshift.mathaxis, text.size.tiny], exclude=0.1)])
        else:
            canvas.stroke(path.line(tail[0], tail[1], head[0], head[1]), [deco.earrow])
    else:
        if string and string[0] == '-':
            canvas.stroke(path.line(head[0], head[1], tail[0], tail[1]), [deco.barrow, deco.curvedtext(string, textattrs=[text.vshift.mathaxis, text.size.tiny], exclude=0.1), color.rgb.red])
        elif string and string[0] != '-':
            canvas.stroke(path.line(head[0], head[1], tail[0], tail[1]), [deco.barrow, deco.curvedtext(string, textattrs=[text.vshift.mathaxis, text.size.tiny], exclude=0.1)])
        else:
            canvas.stroke(path.line(head[0], head[1], tail[0], tail[1]), [deco.barrow])
