// 高斯消元（Gauss-Jordan 全主元消去）· 精确分数运算 · 控制台版
// 编译: g++ -O2 -std=c++17 gauss.cpp -o gauss.exe
#include <algorithm>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#define ISATTY _isatty(_fileno(stdin))
#else
#include <unistd.h>
#define ISATTY isatty(fileno(stdin))
#endif

using namespace std;

/* ================= 分数 ================= */
struct Frac {
    long long n = 0, d = 1;
    Frac() {}
    Frac(long long a, long long b = 1) {
        if (b == 0) { cerr << "错误: 除以零" << endl; exit(1); }
        if (b < 0) { a = -a; b = -b; }
        long long g = std::gcd(a < 0 ? -a : a, b);
        if (g == 0) g = 1;
        n = a / g; d = b / g;
    }
};

[[maybe_unused]] static Frac operator+(Frac x, Frac y) {
    return Frac((long long)((__int128)x.n * y.d + (__int128)y.n * x.d),
                (long long)((__int128)x.d * y.d));
}
static Frac operator-(Frac x, Frac y) {
    return Frac((long long)((__int128)x.n * y.d - (__int128)y.n * x.d),
                (long long)((__int128)x.d * y.d));
}
static Frac operator*(Frac x, Frac y) {
    return Frac((long long)((__int128)x.n * y.n), (long long)((__int128)x.d * y.d));
}
static Frac operator/(Frac x, Frac y) {
    return Frac((long long)((__int128)x.n * y.d), (long long)((__int128)x.d * y.n));
}
static bool isZero(Frac x) { return x.n == 0; }
static bool isOne(Frac x)  { return x.n == 1 && x.d == 1; }
static bool isNeg(Frac x)  { return x.n < 0; }
static Frac neg(Frac x)    { return Frac(-x.n, x.d); }
static bool same(Frac a, Frac b) { return a.n == b.n && a.d == b.d; }

static string str(Frac x) {
    if (x.d == 1) return to_string(x.n);
    return to_string(x.n) + "/" + to_string(x.d);
}

/* 解析输入: 整数 / 小数 / a/b */
static bool parseFrac(const string& s, Frac& out) {
    if (s.empty()) return false;
    size_t slash = s.find('/');
    if (slash != string::npos) {
        try {
            long long a = stoll(s.substr(0, slash));
            long long b = stoll(s.substr(slash + 1));
            if (b == 0) return false;
            out = Frac(a, b);
            return true;
        } catch (...) { return false; }
    }
    size_t dot = s.find('.');
    if (dot != string::npos) {
        try {
            string ip = s.substr(0, dot), fp = s.substr(dot + 1);
            bool neg_ = (!ip.empty() && ip[0] == '-');
            if (neg_) ip = ip.substr(1);
            if (ip.empty()) ip = "0";
            long long den = 1;
            for (size_t i = 0; i < fp.size(); ++i) den *= 10;
            long long num = stoll(ip + fp);
            out = Frac(neg_ ? -num : num, den);
            return true;
        } catch (...) { return false; }
    }
    try {
        out = Frac(stoll(s));
        return true;
    } catch (...) { return false; }
}

/* ================= 一步 ================= */
struct Step {
    string kind;   // 换行 / 消去 / 回代 / 归一
    string op;     // R2 <- R2 + (3/2)*R1
    string note;   // 说明
    vector<vector<Frac>> m;
    int pr = -1, pc = -1;   // 这一步的主元位置
};


static string rowOp(int r, Frac f, int pr) {
    bool plus = isNeg(f);
    Frac ab = plus ? neg(f) : f;
    string c;
    if (!isOne(ab)) c = (ab.d == 1 ? str(ab) : "(" + str(ab) + ")") + "*";
    return "R" + to_string(r + 1) + " <- R" + to_string(r + 1) +
           (plus ? " + " : " - ") + c + "R" + to_string(pr + 1);
}

struct Solution {
    enum Kind { K_UNIQUE, K_INFINITE, K_NONE } kind = K_UNIQUE;
    vector<pair<int, Frac>> vals;          // 唯一解: (列, 值)
    int rank = 0, badRow = -1;
    vector<string> lines;                  // 无穷多解时的通解式子
};

struct Result {
    vector<Step> steps;
    vector<vector<Frac>> rref;
    Solution sol;
};

/* ================= 求解 ================= */
static Result solve(const vector<vector<Frac>>& A0) {
    int m = (int)A0.size(), n = (int)A0[0].size();   // n 列，末列为常数
    vector<vector<Frac>> a = A0;
    Result R;
    vector<pair<int, int>> piv;
    int pr = 0;

    for (int col = 0; col < n - 1 && pr < m; ++col) {
        int sel = -1;
        for (int r = pr; r < m; ++r)
            if (!isZero(a[r][col])) { sel = r; break; }
        if (sel < 0) continue;                       // 该列无主元，跳过

        if (sel != pr) {
            swap(a[pr], a[sel]);
            R.steps.push_back({"换行",
                "R" + to_string(pr + 1) + " <-> R" + to_string(sel + 1),
                "第 " + to_string(col + 1) + " 列主元位置是 0，换一行上来",
                a, pr, col});
        }
        Frac pv = a[pr][col];
        for (int r = pr + 1; r < m; ++r) {
            if (isZero(a[r][col])) continue;
            Frac f = a[r][col] / pv;
            for (int c = 0; c < n; ++c) a[r][c] = a[r][c] - f * a[pr][c];
            R.steps.push_back({"消去", rowOp(r, f, pr),
                "主元 a" + to_string(pr + 1) + to_string(col + 1) + " = " + str(pv) +
                "，把 a" + to_string(r + 1) + to_string(col + 1) + " 打成 0",
                a, pr, col});
        }
        piv.push_back({pr, col});
        ++pr;
    }

    for (int k = (int)piv.size() - 1; k >= 0; --k) {
        int row = piv[k].first, col = piv[k].second;
        for (int r = row - 1; r >= 0; --r) {
            if (isZero(a[r][col])) continue;
            Frac f = a[r][col] / a[row][col];
            for (int c = 0; c < n; ++c) a[r][c] = a[r][c] - f * a[row][c];
            R.steps.push_back({"回代", rowOp(r, f, row),
                "把主元上方的元素清成 0", a, row, col});
        }
    }

    for (auto& p : piv) {
        int row = p.first, col = p.second;
        if (isOne(a[row][col])) continue;
        Frac pv = a[row][col];
        for (int c = 0; c < n; ++c) a[row][c] = a[row][c] / pv;
        string divs = (pv.d == 1 && !isNeg(pv)) ? str(pv) : "(" + str(pv) + ")";
        R.steps.push_back({"归一",
            "R" + to_string(row + 1) + " <- R" + to_string(row + 1) + " / " + divs,
            "主元化成 1，右边那列就是解", a, row, col});
    }

    /* 判解 */
    for (int r = 0; r < m; ++r) {
        bool allZero = true;
        for (int c = 0; c < n - 1; ++c) if (!isZero(a[r][c])) { allZero = false; break; }
        if (allZero && !isZero(a[r][n - 1])) { R.sol.badRow = r; break; }
    }
    R.sol.rank = (int)piv.size();

    if (R.sol.badRow >= 0) {
        R.sol.kind = Solution::K_NONE;
    } else if ((int)piv.size() == n - 1) {
        R.sol.kind = Solution::K_UNIQUE;
        for (auto& p : piv) R.sol.vals.push_back({p.second, a[p.first][n - 1]});
    } else {
        R.sol.kind = Solution::K_INFINITE;
        vector<int> pivCol;
        for (auto& p : piv) pivCol.push_back(p.second);
        vector<int> freeCol;
        for (int c = 0; c < n - 1; ++c)
            if (find(pivCol.begin(), pivCol.end(), c) == pivCol.end()) freeCol.push_back(c);
        vector<string> tname(freeCol.size());
        for (size_t i = 0; i < freeCol.size(); ++i)
            tname[i] = "t" + to_string(i + 1);

        for (auto& p : piv) {
            int row = p.first, col = p.second;
            string s = str(a[row][n - 1]);
            for (size_t i = 0; i < freeCol.size(); ++i) {
                Frac co = neg(a[row][freeCol[i]]);
                if (isZero(co)) continue;
                Frac ab = isNeg(co) ? neg(co) : co;
                s += (isNeg(co) ? " - " : " + ");
                if (!isOne(ab)) s += str(ab) + "*";
                s += tname[i];
            }
            R.sol.lines.push_back("x" + to_string(col + 1) + " = " + s);
        }
        for (size_t i = 0; i < freeCol.size(); ++i)
            R.sol.lines.push_back("x" + to_string(freeCol[i] + 1) + " = " + tname[i] + "  (自由)");
    }

    R.rref = a;
    return R;
}

/* ================= 输出 ================= */
static bool g_color = true;
static const char* C_PIVOT = "\033[1;36m";
static const char* C_CHG   = "\033[1;33m";
static const char* C_DIM   = "\033[2m";
static const char* C_OFF   = "\033[0m";

static vector<int> colWidth(const vector<vector<vector<Frac>>>& mats) {
    int n = (int)mats[0][0].size();
    vector<int> w(n, 1);
    for (auto& m : mats)
        for (auto& row : m)
            for (int c = 0; c < n; ++c)
                w[c] = max(w[c], (int)str(row[c]).size());
    return w;
}

static void printMatrix(const vector<vector<Frac>>& a, const vector<int>& w,
                        int pr, int pc, const vector<vector<Frac>>* prev) {
    int n = (int)a[0].size();
    for (int r = 0; r < (int)a.size(); ++r) {
        cout << "  ";
        for (int c = 0; c < n; ++c) {
            if (c == n - 1) cout << "| ";
            string s = str(a[r][c]);
            bool pivot  = (r == pr && c == pc);
            bool change = prev && !same((*prev)[r][c], a[r][c]);
            if (g_color) {
                if (pivot) cout << C_PIVOT;
                else if (change) cout << C_CHG;
            }
            cout << string(w[c] - s.size(), ' ') << s;
            if (g_color && (pivot || change)) cout << C_OFF;
            cout << "  ";
        }
        cout << "\n";
    }
}

static void printAll(const vector<vector<Frac>>& A, const Result& R, bool stepMode, bool colr) {
    g_color = colr;
    vector<vector<vector<Frac>>> mats;
    mats.push_back(A);
    for (auto& s : R.steps) mats.push_back(s.m);
    vector<int> w = colWidth(mats);

    cout << "\n初始增广矩阵:\n";
    printMatrix(A, w, -1, -1, nullptr);

    const vector<vector<Frac>>* prev = &A;
    for (size_t i = 0; i < R.steps.size(); ++i) {
        const Step& s = R.steps[i];
        if (stepMode) {
            cout << "\n按回车继续 (第 " << i + 1 << " / " << R.steps.size() << " 步)...";
            cout.flush();
            string dummy;
            getline(cin, dummy);
        }
        cout << "\n[" << i + 1 << "/" << R.steps.size() << "] " << s.kind << "   " << s.op << "\n";
        if (!s.note.empty()) cout << "      " << (g_color ? C_DIM : "") << s.note
                                  << (g_color ? C_OFF : "") << "\n";
        printMatrix(s.m, w, s.pr, s.pc, prev);
        prev = &s.m;
    }

    cout << "\n化简结果:\n";
    printMatrix(R.rref, w, -1, -1, nullptr);

    const Solution& so = R.sol;
    cout << "\n";
    if (so.kind == Solution::K_NONE) {
        cout << "结论: 无解。第 " << so.badRow + 1 << " 行化成 0 = "
             << str(R.rref[so.badRow][R.rref[0].size() - 1]) << "，矛盾。\n";
    } else if (so.kind == Solution::K_UNIQUE) {
        cout << "结论: 唯一解（秩 = " << so.rank << "）\n  ";
        for (size_t i = 0; i < so.vals.size(); ++i) {
            if (i) cout << "   ";
            cout << "x" << so.vals[i].first + 1 << " = " << str(so.vals[i].second);
        }
        cout << "\n";
    } else {
        cout << "结论: 有无穷多解（秩 = " << so.rank << " < " << R.rref[0].size() - 1 << "）\n";
        for (auto& l : so.lines) cout << "  " << l << "\n";
    }
}

/* ================= main ================= */
int main(int argc, char** argv) {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD mode = 0;
    if (h != INVALID_HANDLE_VALUE && GetConsoleMode(h, &mode))
        SetConsoleMode(h, mode | 0x0004);   // ENABLE_VIRTUAL_TERMINAL_PROCESSING
#endif
    bool noColor = getenv("NO_COLOR") != nullptr;

    int n = 0;
    cout << "高斯消元（精确分数运算）\n"
         << "增广矩阵大小 n: 请输入方程个数（= 未知数个数），如 3\n> ";
    cout.flush();
    if (!(cin >> n) || n <= 0 || n > 12) {
        cerr << "方程个数需要是 1..12 的整数\n";
        return 1;
    }
    { string rest; getline(cin, rest); }

    cout << "请输入 " << n << " 行，每行 " << n << " 个系数 + 1 个常数（共 " << n + 1
         << " 个数），支持整数/小数/分数，如:\n"
         << "  2 1 -1 8\n  -3 -1 2 -11\n  -2 1 2 -3\n> ";
    cout.flush();

    vector<Frac> vals;
    while ((int)vals.size() < n * (n + 1)) {
        string line;
        if (!getline(cin, line)) break;
        istringstream iss(line);
        string tok;
        while (iss >> tok) {
            Frac v;
            if (!parseFrac(tok, v)) {
                cerr << "无法识别的数: " << tok << "\n";
                return 1;
            }
            vals.push_back(v);
        }
    }
    if ((int)vals.size() < n * (n + 1)) {
        cerr << "数据不够，需要 " << n * (n + 1) << " 个数，只收到 " << vals.size() << " 个\n";
        return 1;
    }

    vector<vector<Frac>> A(n, vector<Frac>(n + 1));
    for (int r = 0; r < n; ++r)
        for (int c = 0; c <= n; ++c) A[r][c] = vals[r * (n + 1) + c];

    bool stepMode = ISATTY != 0;
    for (int i = 1; i < argc; ++i) {
        string a = argv[i];
        if (a == "--all" || a == "-a") stepMode = false;
        if (a == "--step") stepMode = true;
        if (a == "--no-color") noColor = true;
    }

    Result R = solve(A);
    printAll(A, R, stepMode, !noColor);

    if (stepMode) {
        cout << "\n按回车退出...";
        cout.flush();
        string dummy;
        getline(cin, dummy);
    }
    return 0;
}
