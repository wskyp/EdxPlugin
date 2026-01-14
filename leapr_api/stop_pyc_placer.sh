#!/bin/bash
# 如果API_DIR环境变量时空，则退出
if [ -z $API_DIR ]; then
  echo "API_DIR 环境变量是空，请设置！"
  exit
fi
touch $API_DIR/client_result_done
touch $API_DIR/server_result_done
touch $API_DIR/plugin_msg.txt
touch $API_DIR/plugin_msg_done
sleep 3
rm -rf $API_DIR/*