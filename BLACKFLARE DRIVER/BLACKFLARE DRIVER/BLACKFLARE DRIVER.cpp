#include <interception.h>
#include <cstring>
#include <iostream>
#include <windows.h>
#include <thread>
#include <chrono>

extern "C" __declspec(dllexport) void move_mouse(int x, int y);
extern "C" __declspec(dllexport) void mouse_click();
extern "C" __declspec(dllexport) void get_mouse_pos(int* x, int* y);
extern "C" __declspec(dllexport) void slow_down_mouse(bool slow_down, double timeout_seconds);
extern "C" __declspec(dllexport) void set_mouse_position(double x, double y);
extern "C" __declspec(dllexport) void set_detected_key(int key);

void move_mouse(int x, int y);
void mouse_click();
void slow_down_mouse(bool slow_down, double timeout_seconds);
void get_mouse_pos(int* x, int* y);
void set_mouse_position(double x, double y);
void toggle_key_async();
void detect_key_press();

int detected_key = 'A'; // Default key is 'A'

int main() {
    std::thread toggle_thread(toggle_key_async);
    toggle_thread.detach();

    std::thread detect_thread(detect_key_press);
    detect_thread.detach();

    // Add your main logic here
    std::this_thread::sleep_for(std::chrono::seconds(10)); // Simulate some work

    return 0;
}

void move_mouse(int x, int y) {
    InterceptionContext context = interception_create_context();

    InterceptionMouseStroke stroke;
    stroke.state = INTERCEPTION_FILTER_MOUSE_MOVE;
    stroke.flags = 0;
    stroke.rolling = 0;
    stroke.x = x;
    stroke.y = y;
    stroke.information = 0;

    InterceptionStroke strokes[1];
    memcpy(strokes, &stroke, sizeof(strokes));

    interception_send(context, INTERCEPTION_MOUSE(0), strokes, 1);

    interception_destroy_context(context);
}

void mouse_click() {
    InterceptionContext context = interception_create_context();

    InterceptionMouseStroke stroke_down;
    stroke_down.state = INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN;
    stroke_down.flags = 0;
    stroke_down.rolling = 0;
    stroke_down.x = 0;
    stroke_down.y = 0;
    stroke_down.information = 0;

    InterceptionMouseStroke stroke_up;
    stroke_up.state = INTERCEPTION_MOUSE_LEFT_BUTTON_UP;
    stroke_up.flags = 0;
    stroke_up.rolling = 0;
    stroke_up.x = 0;
    stroke_up.y = 0;
    stroke_up.information = 0;

    InterceptionStroke strokes[1];

    memcpy(strokes, &stroke_down, sizeof(strokes));
    interception_send(context, INTERCEPTION_MOUSE(0), strokes, 1);

    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    memcpy(strokes, &stroke_up, sizeof(strokes));
    interception_send(context, INTERCEPTION_MOUSE(0), strokes, 1);

    interception_destroy_context(context);
}

void slow_down_mouse(bool slow_down, double timeout_seconds) {
    InterceptionContext context;
    InterceptionDevice device;
    InterceptionStroke stroke;

    context = interception_create_context();
    interception_set_filter(context, interception_is_mouse, INTERCEPTION_FILTER_MOUSE_MOVE);

    double scalingFactor = 0.5;
    time_t start_time = time(NULL);

    while (interception_receive(context, device = interception_wait(context), &stroke, 1) > 0) {
        if (interception_is_mouse(device)) {
            InterceptionMouseStroke& mstroke = *(InterceptionMouseStroke*)&stroke;

            if (slow_down) {
                mstroke.x *= scalingFactor;
                mstroke.y *= scalingFactor;
            }

            interception_send(context, device, &stroke, 1);
        }

        if (time(NULL) - start_time >= timeout_seconds) {
            break;
        }
    }

    interception_destroy_context(context);
}

void __stdcall get_mouse_pos(int* x, int* y) {
    POINT p;
    if (GetCursorPos(&p)) {
        *x = p.x;
        *y = p.y;
    }
}

void set_mouse_position(double x, double y) {
    InterceptionContext context = interception_create_context();

    InterceptionMouseStroke stroke;
    stroke.state = INTERCEPTION_FILTER_MOUSE_MOVE;
    stroke.flags = 0;
    stroke.rolling = 0;
    stroke.x = x;
    stroke.y = y;
    stroke.information = 0;

    InterceptionStroke strokes[1];
    memcpy(strokes, &stroke, sizeof(strokes));

    interception_send(context, INTERCEPTION_MOUSE(0), strokes, 1);

    interception_destroy_context(context);
}

void set_detected_key(int key) {
    detected_key = key;
}

void toggle_key_async() {
    while (true) {
        // Simulate a key press (e.g., 'A' key)
        keybd_event(detected_key, 0, 0, 0);  // Press the detected key
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Debounce
        keybd_event(detected_key, 0, KEYEVENTF_KEYUP, 0);  // Release the detected key

        // Wait before next toggle
        std::this_thread::sleep_for(std::chrono::seconds(1)); // Adjust the interval as needed
    }
}

void detect_key_press() {
    while (true) {
        if (GetAsyncKeyState(detected_key) & 0x8000) {
            std::cout << "Hello World" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(500)); // Debounce
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Polling delay
    }
}
