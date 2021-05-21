def eye_comparison(b, u):
    response = '眼部分析结果：'
    diff = u - b

    if diff[0] < 0:
        response += '眼型分析：你的眼睛太小，需要化大'
    else:
        response += '眼型分析：你的眼睛已经够大了'

    response += '眼宽分析：你的眼睛上下宽度得分{0:.2f}, 美女得分{1:.2f}'.format(u[1], b[1])
    if diff[1] < 0:
        response += '眼宽分析：你的眼睛上下宽度需要提升'
    else:
        response += '眼宽分析：你的眼好宽哦'

    response += '眼长分析：你的眼睛长度得分{0:.2f}, 美女得分{1:.2f}'.format(u[2], b[2])
    if diff[2] < 0:
        response += '眼长分析：你的眼睛长度需要提升，建议用眼线笔化长'
    else:
        response += '眼长分析：你的眼好长哦'

    response += '眼间距分析：你的眼间距得分{0:.2f}, 美女得分{1:.2f}'.format(u[3], b[3])
    if diff[3] > 0:
        response += '眼间距分析：你的眼间距需要缩短，建议修饰内眼角'
    else:
        response += '眼间距分析：你的眼间距好窄哦'
    return response, diff


def nose_comparison(b, u):
    response = '鼻部分析结果：'
    diff = u - b
    
    if diff[0] < 0:
        response += '鼻型分析：你的鼻子属于宽鼻型，需要鼻影修饰'
    else:
        response += '鼻型分析：你的鼻子标准偏窄，很棒，不需要太多修饰~'

    response += '鼻翼分析：你的鼻翼宽度得分{0:.2f}, 美女得分{1:.2f}'.format(u[1], b[1])
    if diff[1] < 0:
        response += '鼻翼分析：你的鼻翼宽度较小，很理想~'
    else:
        response += '鼻翼分析：你的鼻翼较宽，建议在鼻翼两侧加阴影，同时在鼻头出加高光以修饰鼻头鼻翼'

    response += '鼻长分析：你的鼻长得分{0:.2f}, 美女得分{1:.2f}'.format(u[2], b[2])
    if diff[2] < 0:
        response += '鼻长分析：你的鼻子较短，建议在山根处加上鼻影，并延伸至鼻头上方，使用高光部分提亮，一定记得晕染开哦'
        response += '鼻长分析：你的鼻子较长，鼻梁高光不宜画得太长，在山根附近加高光即可，并且可以用阴影来缩短鼻头'
        
    return response, diff


def lip_comparison(b, u):
    response = '唇部分析结果：'
    diff = u - b

    if diff[0] < 0:
        response += '唇型分析：你的唇形偏薄'
    else:
        response += '唇型分析：你的唇形偏厚'

    response += '人中长度分析：你的人中长度得分{0:.2f}, 美女得分{1:.2f}'.format(u[1], b[1])
    if diff[1] < 0:
        response += '人中长度分析：你的人中较短'
    else:
        response += '人中长度分析：你的人中较长，建议在上唇边缘上方和人中突起处用高光修饰，并在涂唇彩时略微超出本来的边缘，强调唇线'

    response += '下巴长度分析：你的下巴长度得分{0:.2f}, 美女得分{1:.2f}'.format(u[2], b[2])
    if diff[2] < 0:
        response += '下巴长度分析：你的下巴较短，建议在下巴中央用高光强调，并从下巴最低处斜向上45°用高光修饰'
    else:
        response += '下巴长度分析：你的下巴较长，可以考虑在下巴最低处用阴影修饰'

    response += '唇厚度分析：你的唇厚度得分{0:.2f}, 美女得分{1:.2f}'.format(u[3], b[3])
    if diff[3] > 0:
        response += '唇厚度分析：你的唇部较厚，很性感哦'
    else:
        response += '唇厚度分析：你的唇部较薄，可以考虑用唇釉提升饱满度'
    return response, diff