#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"

#define LED_PIN 2
#define LED_PIN2 3

static void pulse_led(unsigned int on_ms, unsigned int off_ms)
{
    gpio_put(LED_PIN, 1);
    gpio_put(LED_PIN2, 1);
    sleep_ms(on_ms);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN2, 0);
    sleep_ms(off_ms);
}

static void handle_command(const char *command)
{
    if (strcmp(command, "HIT") == 0) {
        pulse_led(120, 40);
        printf("OK HIT\n");
    } else if (strcmp(command, "MISS") == 0) {
        pulse_led(40, 40);
        pulse_led(40, 0);
        printf("OK MISS\n");
    }

    fflush(stdout);
}

int main()
{
    stdio_init_all();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);

    gpio_init(LED_PIN2);
    gpio_set_dir(LED_PIN2, GPIO_OUT);
    gpio_put(LED_PIN2, 0);

    printf("Pico serial demo ready\n");
    printf("Commands: ON, OFF, TOGGLE, PULSE, HIT, MISS, SCORE <n>, READY, GAME_OVER, STATUS\n");

    char command[32];
    size_t command_length = 0;

    while (true) {
        int character = getchar_timeout_us(0);

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
