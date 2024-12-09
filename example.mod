// Simple model example
int n = 2;
dvar float+ x[1..n];

minimize x[1] + x[2];

subject to {
    x[1] + x[2] <= 10;
}