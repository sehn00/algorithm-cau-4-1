#include <bits/stdc++.h>
using namespace std;

int partition_last(vector<int>& data, int left, int right);
int partition_by_value(vector<int>& data, int left, int right, int pivot_value);
int get_median(vector<int>& data, int left, int right);
int select_pivot_bfprt(vector<int>& data, int left, int right);

int quick_select(vector<int>& data, int left, int right, int target);
int bfprt(vector<int>& data, int left, int right, int target);

int main() {
    const int N = 10000;
    int target = 0;
    vector<int> data;

    for (int i = 0; i < N; i++) {
        data.push_back(i);
    }

    random_device rd;
    mt19937 g(rd());

    shuffle(data.begin(), data.end(), g);
    // sort(data.begin(), data.end());   // 주석 해제 시 오름차순 정렬

    vector<int> data_quick = data;
    vector<int> data_bfprt = data;

    auto start_time = chrono::high_resolution_clock::now();
    int result_quick = quick_select(data_quick, 0, N - 1, target);
    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed_quick = end_time - start_time;

    cout << "[Quick] 결과: " << result_quick << '\n';
    cout << "[Quick] 소요 시간: " << fixed << setprecision(6)
         << elapsed_quick.count() << " 초\n";

    start_time = chrono::high_resolution_clock::now();
    int result_bfprt = bfprt(data_bfprt, 0, N - 1, target);
    end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed_bfprt = end_time - start_time;

    cout << "[BFPRT] 결과: " << result_bfprt << '\n';
    cout << "[BFPRT] 소요 시간: " << fixed << setprecision(6)
         << elapsed_bfprt.count() << " 초\n";

    return 0;
}

int partition_last(vector<int>& data, int left, int right) {
    int pivot = data[right];
    int i = left;

    for (int j = left; j < right; j++) {
        if (data[j] < pivot) {
            swap(data[i], data[j]);
            i++;
        }
    }

    swap(data[i], data[right]);
    return i;
}

int quick_select(vector<int>& data, int left, int right, int target) {
    if (left == right) return data[left];

    int pivot_index = partition_last(data, left, right);

    if (pivot_index == target) return data[pivot_index];
    else if (target < pivot_index)
        return quick_select(data, left, pivot_index - 1, target);
    else
        return quick_select(data, pivot_index + 1, right, target);
}

int partition_by_value(vector<int>& data, int left, int right, int pivot_value) {
    int pivot_index = left;

    for (int i = left; i <= right; i++) {
        if (data[i] == pivot_value) {
            pivot_index = i;
            break;
        }
    }

    swap(data[pivot_index], data[right]);

    int i = left;
    for (int j = left; j < right; j++) {
        if (data[j] < pivot_value) {
            swap(data[i], data[j]);
            i++;
        }
    }

    swap(data[i], data[right]);
    return i;
}

int get_median(vector<int>& data, int left, int right) {
    sort(data.begin() + left, data.begin() + right + 1);
    int mid = left + (right - left) / 2;
    return data[mid];
}

int select_pivot_bfprt(vector<int>& data, int left, int right) {
    int n = right - left + 1;

    if (n <= 5) {
        return get_median(data, left, right);
    }

    vector<int> medians;

    for (int i = left; i <= right; i += 5) {
        int group_right = min(i + 4, right);
        int median = get_median(data, i, group_right);
        medians.push_back(median);
    }

    int median_target = (medians.size() - 1) / 2;
    return bfprt(medians, 0, (int)medians.size() - 1, median_target);
}

int bfprt(vector<int>& data, int left, int right, int target) {
    if (left == right) return data[left];

    int pivot_value = select_pivot_bfprt(data, left, right);
    int pivot_index = partition_by_value(data, left, right, pivot_value);

    if (pivot_index == target) return data[pivot_index];
    else if (target < pivot_index)
        return bfprt(data, left, pivot_index - 1, target);
    else
        return bfprt(data, pivot_index + 1, right, target);
}