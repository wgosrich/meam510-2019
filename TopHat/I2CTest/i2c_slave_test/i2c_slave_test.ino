/* i2c_slave_test - Example
 *  Slave i2c expecting slave ESP32 on i2c_master_test
 *  modified from 
   https://github.com/espressif/esp-idf/tree/master/examples/peripherals/i2c/i2c_self_test
   For other examples please check:
   https://github.com/espressif/esp-idf/tree/master/examples

    Attach SCL wire to GPIO 26, and  SDA to GPIO 25
   
   See README.md file to get detailed usage of this example.
   This example code is in the Public Domain (or CC0 licensed, at your option.)
   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"
#include "sdkconfig.h"

#define _I2C_NUMBER(num) I2C_NUM_##num
#define I2C_NUMBER(num) _I2C_NUMBER(num)

#define DATA_LENGTH 128                  /*!< Data buffer length of test buffer */
#define RW_TEST_LENGTH 128               /*!< Data length for r/w test, [0,DATA_LENGTH] */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000 /*!< delay time between different test items */

#define I2C_SLAVE_SCL_IO (gpio_num_t)33               /*!< gpio number for i2c slave clock */
#define I2C_SLAVE_SDA_IO (gpio_num_t)25               /*!< gpio number for i2c slave data */
#define I2C_SLAVE_NUM I2C_NUMBER(0) /*!< I2C port number for slave dev */
#define I2C_SLAVE_TX_BUF_LEN (2* DATA_LENGTH)              /*!< I2C slave tx buffer size */
#define I2C_SLAVE_RX_BUF_LEN (2 * DATA_LENGTH)              /*!< I2C slave rx buffer size */

#define CONFIG_I2C_SLAVE_ADDRESS 0x28
#define ESP_SLAVE_ADDR CONFIG_I2C_SLAVE_ADDRESS /*!< ESP32 slave address, you can set any 7bit value */

/**
 * @brief i2c slave initialization
 */
static esp_err_t i2c_slave_init()
{
    i2c_port_t i2c_slave_port = I2C_SLAVE_NUM;
    i2c_config_t conf_slave;
    conf_slave.sda_io_num = I2C_SLAVE_SDA_IO;
    conf_slave.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.scl_io_num = I2C_SLAVE_SCL_IO;
    conf_slave.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.mode = I2C_MODE_SLAVE;
    conf_slave.slave.addr_10bit_en = 0;
    conf_slave.slave.slave_addr = ESP_SLAVE_ADDR;
    i2c_param_config(i2c_slave_port, &conf_slave);
    return i2c_driver_install(i2c_slave_port, conf_slave.mode,
                              I2C_SLAVE_RX_BUF_LEN,
                              I2C_SLAVE_TX_BUF_LEN, 0);
}

/**
 * @brief test function to show buffer
 */
static void disp_buf(uint8_t *buf, int len)
{
    int i;
    for (i = 0; i < len; i++) {
        Serial.printf("%02x ", buf[i]);
        if ((i + 1) % 16 == 0) {
            Serial.printf("\n");
        }
    }
    Serial.printf("\n");
}

uint8_t data[DATA_LENGTH]  ;
uint8_t data_wr[DATA_LENGTH];

uint8_t count;

static void i2c_write_buffer() 
{
    int ret;
    
    data_wr[0] = count++; // just to see numbers change in the data
    
    if ( i2c_slave_write_buffer(I2C_SLAVE_NUM, data_wr, RW_TEST_LENGTH, 10 / portTICK_RATE_MS) ) {
      Serial.println("buffer written");
    }
    else {
      Serial.println("i2c slave tx buffer full"); // should never happen if we only send after each request to read
    }
}


int i2c_read_test()  // returns 0 if nothing has been written to slave
{       int datasize, ret;
        long starttime = micros();
        datasize = i2c_slave_read_buffer(I2C_SLAVE_NUM, data, RW_TEST_LENGTH, 0/portTICK_RATE_MS); // last term is wait time 0/portTICK_RATE_MS means don't wait  
        if (datasize > 0) {
            Serial.printf("---- Slave read: [%d] bytes ----\n", datasize);
            disp_buf(data, datasize);
        }
        else Serial.printf("------ No data to read in %d us \n", micros()-starttime);
        return (datasize);
}

void setup() {
  
  Serial.begin(115200);  // put your setup code here, to run once:
  pinMode (2,OUTPUT);
  
  for (int i=0; i<DATA_LENGTH; i++) {
    data_wr[i] = i;  // put some structured data, just so we can verify it's there
  }
  strcpy((char *)data_wr," This is some text ");
  
  ESP_ERROR_CHECK(i2c_slave_init());
}

void loop() {
    if (i2c_read_test() > 0) {
      delay(400); 
      i2c_write_buffer();
    }
    digitalWrite(2,LOW);
    delay(400);
    digitalWrite(2,HIGH);
    Serial.println(count);
}
