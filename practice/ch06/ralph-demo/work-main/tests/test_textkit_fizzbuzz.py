from src.textkit import fizzbuzz


def test_fizzbuzz_basic_sequence():
    # 基本案例：1..5 只有 Fizz（3）與 Buzz（5）
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_fizzbuzz_at_multiples_of_15():
    # 同時是 3 與 5 倍數的數字應輸出 FizzBuzz，而非 Fizz 或 Buzz
    result = fizzbuzz(15)
    assert result[14] == "FizzBuzz"
    assert result[2] == "Fizz"
    assert result[4] == "Buzz"


def test_fizzbuzz_boundary_non_positive_returns_empty():
    # 邊界案例：n <= 0 回傳空 list
    assert fizzbuzz(0) == []
    assert fizzbuzz(-3) == []
    assert fizzbuzz(1) == ["1"]
