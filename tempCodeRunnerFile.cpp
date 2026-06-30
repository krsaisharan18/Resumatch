// Online C++ compiler to run C++ program online
#include <bits/stdc++.h>

int main() {
    // Write C++ code here
    int n=5;
    string line;
    getline(cin,line);
    stringstream ss(line);
    vector<int> arr;
    string x;
    while(getline(ss,x," ")){
        arr.push_back((stoi)x);
    }
    for(int a: arr){
        print(a);
    }

    return 0;
}