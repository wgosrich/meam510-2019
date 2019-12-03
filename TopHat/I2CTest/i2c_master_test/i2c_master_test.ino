/* i2c_master_test - Example
 *  Master i2c expecting slave ESP32 on i2c_slave_test
 *  modified from 
   https://github.com/espressif/esp-idf/tree/master/examples/peripherals/i2c/i2c_self_test
   For other examples please check:
   https://github.com/espressif/esp-idf/tree/master/examples

    Attach SCL wire to GPIO 19, and  SDA to GPIO 18
   
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

static const char *TAG = "i2c-example";

#define _I2C_NUMBER(num) I2C_NUM_##num
#define I2C_NUMBER(num) _I2C_NUMBER(num)

#define DATA_LENGTH 128                  /*!< Data buffer length of test buffer */
#define RW_TEST_LENGTH 16               /*!< Data length for r/w test, [0,DATA_LENGTH] */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1500 /*!< delay time between different test items */

#define I2C_MASTER_SCL_IO (gpio_num_t)33             /*!< gpio number for I2C master clock */
#define I2C_MASTER_SDA_IO (gpio_num_t)25               /*!< gpio number for I2C master data  */
#define I2C_MASTER_NUM I2C_NUMBER(1) /*!< I2C port number for master dev */
#define I2C_MASTER_FREQ_HZ 100000        /*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE 0                           /*!< I2C master doesn't need buffer */
#define I2C_MASTER_RX_BUF_DISABLE 0                           /*!< I2C master doesn't need buffer */

#define CONFIG_I2C_SLAVE_ADDRESS 0x28
#define ESP_SLAVE_ADDR CONFIG_I2C_SLAVE_ADDRESS /*!< ESP32 slave address, you can set any 7bit value */
#define WRITE_BIT I2C_MASTER_WRITE              /*!< I2C master write */
#define READ_BIT I2C_MASTER_READ                /*!< I2C master read */
#define ACK_CHECK_EN 0x1                        /*!< I2C master will check ack from slave*/
#define ACK_CHECK_DIS 0x0                       /*!< I2C master will not check ack from slave */
#define ACK_VAL I2C_MASTER_ACK                             /*!< I2C ack value */
#define NACK_VAL I2C_MASTER_NACK                           /*!< I2C nack value */

/**
 * @brief test code to read esp-i2c-slave
 *        We need to fill the buffer of esp slave device, then master can read them out.
 *
 * _______________________________________________________________________________________
 * | start | slave_addr + rd_bit +ack | read n-1 bytes + ack | read 1 byte + nack | stop |
 * --------|--------------------------|----------------------|--------------------|------|
 *
 */
static esp_err_t i2c_master_read_slave(i2c_port_t i2c_num, uint8_t *data_rd, size_t nsize)
{
    if (nsize == 0) {
        return ESP_OK;
    }
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (ESP_SLAVE_ADDR << 1) | READ_BIT, ACK_CHECK_EN); 
    if (nsize > 1) {
        i2c_master_read(cmd, data_rd, nsize - 1, ACK_VAL);
    }
    i2c_master_read_byte(cmd, data_rd + nsize - 1, NACK_VAL);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, 1000 / portTICK_RATE_MS); // send all queued commands
    i2c_cmd_link_delete(cmd);
    return ret;
}

/**
 * @brief Test code to write esp-i2c-slave
 *        Master device write data to slave(both esp32),
 *        the data will be stored in slave buffer.
 *        We can read them out from slave buffer.
 *
 * ___________________________________________________________________
 * | start | slave_addr + wr_bit + ack | write n bytes + ack  | stop |
 * --------|---------------------------|----------------------|------|
 *
 */
static esp_err_t i2c_master_write_slave(i2c_port_t i2c_num, uint8_t *data_wr, size_t nsize)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (ESP_SLAVE_ADDR << 1) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write(cmd, data_wr, nsize, ACK_CHECK_EN);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, 1000 / portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}


/**
 * @brief i2c master initialization
 */
static esp_err_t i2c_master_init()
{
    i2c_port_t i2c_master_port = I2C_MASTER_NUM;
    i2c_config_t conf;
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = I2C_MASTER_SDA_IO;
    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf.scl_io_num = I2C_MASTER_SCL_IO;
    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = I2C_MASTER_FREQ_HZ;
    i2c_param_config(i2c_master_port, &conf);
    return i2c_driver_install(i2c_master_port, conf.mode,
                              I2C_MASTER_RX_BUF_DISABLE,
                              I2C_MASTER_TX_BUF_DISABLE, 0);
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

uint8_t data_wr[DATA_LENGTH];
uint8_t data_rd[DATA_LENGTH];

static void i2c_read_test()
{
  int ret;

  ret = i2c_master_read_slave(I2C_MASTER_NUM, data_rd, DATA_LENGTH);

  if (ret == ESP_ERR_TIMEOUT) {
    ESP_LOGE(TAG, "I2C Timeout");
    Serial.println("I2C Timeout");
  } else if (ret == ESP_OK) {
    Serial.printf(" MASTER READ FROM SLAVE ******\n");
    disp_buf(data_rd, DATA_LENGTH);
    digitalWrite(2,LOW);
  } else {
    ESP_LOGW(TAG, " %s: Master read slave error, IO not connected...\n",
             esp_err_to_name(ret));
  }
}

static void i2c_write_test()
{ 
  int ret;
                                                                             
  ret = i2c_master_write_slave(I2C_MASTER_NUM, data_wr, RW_TEST_LENGTH);
  if (ret == ESP_ERR_TIMEOUT) {
    ESP_LOGE(TAG, "I2C Timeout");
  } else if (ret == ESP_OK) {
    Serial.printf(" MASTER WRITE TO SLAVE\n");
    disp_buf(data_wr, RW_TEST_LENGTH);
  } else {
    ESP_LOGW(TAG, "%s: Master write slave error, IO not connected....\n",
            esp_err_to_name(ret));
  }
}

void setup() {
  Serial.begin(115200);  // put your setup code here, to run once:
  pinMode(2, OUTPUT);
  for (int i = 0; i < DATA_LENGTH; i++) {
    data_wr[i] = i*2;
  }
  ESP_ERROR_CHECK(i2c_master_init());
}

void loop() {
    i2c_read_test();
    delay(1000);
    digitalWrite(2,LOW);
    i2c_write_test();
    delay(1000);
    digitalWrite(2,HIGH);
}
