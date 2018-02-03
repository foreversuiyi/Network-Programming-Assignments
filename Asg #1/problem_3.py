def problem_3(nums):
    max_sum = 0
    for i in range(1, len(nums)-1):
        i_sum = sum(nums[i-1:i+2])
        max_sum = max(max_sum, i_sum)
    return max_sum


if __name__ == '__main__':
    nums = input("Enter your list: ")
    nums = [int(x) for x in nums.split(',')]
    print(nums)
    try:
        print(problem_3(nums))
    except Exception as err:
        print("Error: ", err)

