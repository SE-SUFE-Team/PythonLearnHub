def longestPalindrome(s: str) -> str:
    n = len(s)
    ans_left = ans_right = 0

    # 奇回文串
    for i in range(n):
        l = r = i
        while l >= 0 and r < n and s[l] == s[r]:
            l -= 1
            r += 1
        # 循环结束后，s[l+1] 到 s[r-1] 是回文串
        if r - l - 1 > ans_right - ans_left:
            ans_left, ans_right = l + 1, r  # 左闭右开区间

    # 偶回文串
    for i in range(n - 1):
        l, r = i, i + 1
        while l >= 0 and r < n and s[l] == s[r]:
            l -= 1
            r += 1
        if r - l - 1 > ans_right - ans_left:
            ans_left, ans_right = l + 1, r  # 左闭右开区间

    return s[ans_left: ans_right]


def myPow(x: float, n: int) -> float:
    if n < 0:
        return myPow(1 / x, -n)
    if n == 0:
        return 1.0
    return round(myPow(x, n // 2) ** 2 * (x if n % 2 else 1.0), 5)


def maxRotateFunction(nums: list[int]) -> int:
    f, n, numSum = 0, len(nums), sum(nums)
    for i, num in enumerate(nums):
        f += i * num
    res = f
    for i in range(n - 1, 0, -1):
        f = f + numSum - n * nums[i]
        res = max(res, f)
    return res


def twoSum(nums: list[int], target: int) -> list[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]

    return []


def subsets(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    ans = []
    path = []

    def dfs(i: int) -> None:
        if i == n:  # 子集构造完毕
            ans.append(path.copy())  # 复制 path，也可以写 path[:]
            return

        # 不选 nums[i]
        dfs(i + 1)

        # 选 nums[i]
        path.append(nums[i])
        dfs(i + 1)
        path.pop()  # 恢复现场

    dfs(0)
    return ans
