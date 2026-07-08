#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"

//nivel 5 
#define LED_PIN0 18
#define LED_PIN1 1
//nivel 3
#define LED_PIN2 2
#define LED_PIN3 3
#define LED_PIN4 4
//nivel 4
#define LED_PIN5 5
#define LED_PIN7 7
#define LED_PIN8 8

//nivel 2
#define LED_PIN6 6
#define LED_PIN9 9
#define LED_PIN10 10
#define LED_PIN11 11

//nivel 1
#define LED_PIN12 12
#define LED_PIN13 13
#define LED_PIN14 16
#define LED_PIN15 17

static const int level_pins[5][4] = {
    {LED_PIN12, LED_PIN13, LED_PIN14, LED_PIN15},
    {LED_PIN6, LED_PIN9, LED_PIN10, LED_PIN11},
    {LED_PIN2, LED_PIN3, LED_PIN4},
    {LED_PIN5, LED_PIN7, LED_PIN8},
    {LED_PIN0, LED_PIN1},
};

static const int all_led_pins[] = {
    LED_PIN0, LED_PIN1, LED_PIN2, LED_PIN3, LED_PIN4,
    LED_PIN5, LED_PIN6, LED_PIN7, LED_PIN8, LED_PIN9,
    LED_PIN10, LED_PIN11, LED_PIN12, LED_PIN13, LED_PIN14, LED_PIN15
};

static void init_led_pin(int pin)
{
    gpio_init(pin);
    gpio_set_dir(pin, GPIO_OUT);
    gpio_put(pin, 0);
}

static void init_leds(void)
{
    init_led_pin(LED_PIN0);
    init_led_pin(LED_PIN1);
    init_led_pin(LED_PIN2);
    init_led_pin(LED_PIN3);
    init_led_pin(LED_PIN4);
    init_led_pin(LED_PIN5);
    init_led_pin(LED_PIN6);
    init_led_pin(LED_PIN7);
    init_led_pin(LED_PIN8);
    init_led_pin(LED_PIN9);
    init_led_pin(LED_PIN10);
    init_led_pin(LED_PIN11);
    init_led_pin(LED_PIN12);
    init_led_pin(LED_PIN13);
    init_led_pin(LED_PIN14);
    init_led_pin(LED_PIN15);
}

static void clear_all_leds(void)
{
    for (size_t i = 0; i < sizeof(all_led_pins) / sizeof(all_led_pins[0]); ++i) {
        gpio_put(all_led_pins[i], 0);
    }
}

static void set_level(int level, bool on)
{
    if (level < 1 || level > 5) {
        return;
    }

    const int *pins = level_pins[level - 1];
    size_t count = sizeof(level_pins[0]) / sizeof(level_pins[0][0]);

    for (size_t i = 0; i < count; ++i) {
        gpio_put(pins[i], on ? 1 : 0);
    }
}

static void toggle_level(int level)
{
    if (level < 1 || level > 5) {
        return;
    }

    const int *pins = level_pins[level - 1];
    size_t count = sizeof(level_pins[0]) / sizeof(level_pins[0][0]);
    bool currently_on = gpio_get(pins[0]);

    for (size_t i = 0; i < count; ++i) {
        gpio_put(pins[i], currently_on ? 0 : 1);
    }
}

static void handle_command(const char *command)
{
    char buffer[32];
    char action[16] = "";
    int level = 0;

    strncpy(buffer, command, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    for (char *p = buffer; *p != '\0'; ++p) {
        *p = (char)toupper((unsigned char)*p);
    }

    if (strcmp(buffer, "CLEAR") == 0 || strcmp(buffer, "ALL OFF") == 0 || strcmp(buffer, "ALLOFF") == 0) {
        clear_all_leds();
        printf("OK CLEAR\n");
        fflush(stdout);
        return;
    }

    if (sscanf(buffer, "LEVEL%d %15s", &level, action) == 2 ||
        sscanf(buffer, "L%d %15s", &level, action) == 2 ||
        sscanf(buffer, "%d %15s", &level, action) == 2) {
        // parsed
    } else if (sscanf(buffer, "LEVEL%d", &level) == 1 ||
               sscanf(buffer, "L%d", &level) == 1 ||
               sscanf(buffer, "%d", &level) == 1) {
        action[0] = '\0';
    } else {
        printf("ERR Unknown command\n");
        fflush(stdout);
        return;
    }

    if (level < 1 || level > 5) {
        printf("ERR Invalid level\n");
        fflush(stdout);
        return;
    }

    if (strcmp(action, "ON") == 0) {
        set_level(level, true);
        printf("OK LEVEL %d ON\n", level);
    } else if (strcmp(action, "OFF") == 0) {
        set_level(level, false);
        printf("OK LEVEL %d OFF\n", level);
    } else {
        toggle_level(level);
        printf("OK LEVEL %d TOGGLE\n", level);
    }

    fflush(stdout);
}

int main()
{
    stdio_init_all();
    init_leds();

    printf("Pico serial LED control ready\n");
    printf("Commands: LEVEL1/2/3/4/5 ON|OFF|TOGGLE, CLEAR, or 1..5\n");
    fflush(stdout);

    char command[32];
    size_t command_length = 0;

    while (true) {
        int character = getchar_timeout_us(1000);

        if (character == PICO_ERROR_TIMEOUT) {
            tight_loop_contents();
            continue;
        }

        if (character == '\r' || character == '\n') {
            if (command_length > 0) {
                command[command_length] = '\0';
                handle_command(command);
                command_length = 0;
            }
            continue;
        }

        if (command_length < sizeof(command) - 1) {
            command[command_length++] = (char)character;
        } else {
            command_length = 0;
            printf("ERR Command too long\n");
            fflush(stdout);
        }
    }
}
