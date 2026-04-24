import time
import random

import sys
sys.setrecursionlimit(20000)

def partition_last(data, left, right):
    pivot = data[right]
    i = left

    for j in range(left, right):
        if data[j] < pivot:
            data[i], data[j] = data[j], data[i]
            i += 1

    data[i], data[right] = data[right], data[i]
    return i


def quick_select(data, left, right, target):
    if left == right:
        return data[left]

    pivot_index = partition_last(data, left, right)

    if pivot_index == target:
        return data[pivot_index]
    elif target < pivot_index:
        return quick_select(data, left, pivot_index - 1, target)
    else:
        return quick_select(data, pivot_index + 1, right, target)


def partition_by_value(data, left, right, pivot_value):
    pivot_index = left

    for i in range(left, right + 1):
        if data[i] == pivot_value:
            pivot_index = i
            break

    data[pivot_index], data[right] = data[right], data[pivot_index]

    i = left
    for j in range(left, right):
        if data[j] < pivot_value:
            data[i], data[j] = data[j], data[i]
            i += 1

    data[i], data[right] = data[right], data[i]
    return i


def get_median(data, left, right):
    data[left:right + 1] = sorted(data[left:right + 1])
    mid = left + (right - left) // 2
    return data[mid]


def select_pivot_bfprt(data, left, right):
    n = right - left + 1

    if n <= 5:
        return get_median(data, left, right)

    medians = []

    for i in range(left, right + 1, 5):
        group_right = min(i + 4, right)
        median = get_median(data, i, group_right)
        medians.append(median)

    median_target = (len(medians) - 1) // 2
    return bfprt(medians, 0, len(medians) - 1, median_target)


def bfprt(data, left, right, target):
    if left == right:
        return data[left]

    pivot_value = select_pivot_bfprt(data, left, right)
    pivot_index = partition_by_value(data, left, right, pivot_value)

    if pivot_index == target:
        return data[pivot_index]
    elif target < pivot_index:
        return bfprt(data, left, pivot_index - 1, target)
    else:
        return bfprt(data, pivot_index + 1, right, target)


N = 10000
target = 0
data = list(range(N))

random.shuffle(data)
data.sort()  # 주석 해제 시 오름차순 정렬

data_quick = data.copy()
data_bfprt = data.copy()

start_time = time.time()
result_quick = quick_select(data_quick, 0, N - 1, target)
end_time = time.time()

print(f"[Quick] 결과: {result_quick}")
print(f"[Quick] 소요 시간: {end_time - start_time:.4f} 초")

start_time = time.time()
result_bfprt = bfprt(data_bfprt, 0, N - 1, target)
end_time = time.time()

print(f"[BFPRT] 결과: {result_bfprt}")
print(f"[BFPRT] 소요 시간: {end_time - start_time:.4f} 초")