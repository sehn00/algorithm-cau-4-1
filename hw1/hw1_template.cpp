#include <bits/stdc++.h>
using namespace std;

int quick_select(vector<int>& data, int left, int right, int target);
int bfprt(vector<int>& data, int left, int right, int target);

int main() {
    const int N = 10000;
    int target = 0;
    vector<int> data;

    for (int i = 0; i < N; i++) {
        data.push_back(i);
    }

    random_device rd;   // random_device 클래스의 난수 시드 객체 rd 생성
    mt19937 g(rd());    // 시드 값으로 mt19937 클래스의 난수 생성기 g 초기화

    shuffle(data.begin(), data.end(), g);
    // sort(data.begin(), data.end());   // 주석 해제 시 오름차순 정렬

    vector<int> data_quick = data;
    vector<int> data_bfprt = data;

    auto start_time = chrono::high_resolution_clock::now();
    int result_quick = quick_select(data_quick, 0, N - 1, target);   // 구현 필요
    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed_quick = end_time - start_time;

    cout << "[Quick] 결과: " << result_quick << '\n';
    cout << "[Quick] 소요 시간: " << fixed << setprecision(6)
         << elapsed_quick.count() << " 초\n";

    start_time = chrono::high_resolution_clock::now();
    int result_bfprt = bfprt(data_bfprt, 0, N - 1, target);   // 구현 필요
    end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed_bfprt = end_time - start_time;

    cout << "[BFPRT] 결과: " << result_bfprt << '\n';
    cout << "[BFPRT] 소요 시간: " << fixed << setprecision(6)
         << elapsed_bfprt.count() << " 초\n";

    return 0;
}

// 구현 필요
int quick_select(vector<int>& data, int left, int right, int target) {
    return -1;
}

// 구현 필요
int bfprt(vector<int>& data, int left, int right, int target) {
    return -1;
}