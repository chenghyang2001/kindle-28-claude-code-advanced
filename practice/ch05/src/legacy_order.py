"""舊介面相容層：保留 calc() 給既有呼叫者，實際計算委派給 pricing 模組。"""
import pricing


def calc(o, t=None):
    """相容舊簽名；新程式請直接用 pricing.calculate。"""
    return pricing.calculate(o, t)
