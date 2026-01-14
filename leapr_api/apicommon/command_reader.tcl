# 这个脚本主要是EDA读取，用来后续AI工具给EDA工具喂命令的
# 设置脚本交互目录
set api_dir /data/wskyp/cases/top_ASAP7/api
puts "api dir is ${api_dir}"
# 写一个死循环，不断读取目录下是否有client_result文件
proc monitor_client_result {} {
    global api_dir
    set target_dir "${api_dir}"
    puts "开始监控 client_result 文件..."

    while {1} {
        set client_result_path [file join $target_dir "client_result_done"]
        # 检查 client_result 文件是否存在
        if {[file exists $client_result_path]} {
            puts "检测到 client_result_done 文件"

            # 执行目录下的 command.tcl
            set command_path [file join $target_dir "command.tcl"]
            if {[file exists $command_path]} {
                # 执行命令,添加异常保护
                try {
                    puts "执行 command.tcl $command_path"
                    source /data/wskyp/cases/top_ASAP7/api/command.tcl
                } on error {errorMsg options} {
                    puts "execute failed"
                } on ok {} {
                    puts "execute success"
                }
            } else {
                puts "警告: command.tcl 文件不存在"
            }
            # 删除 client_result_done 文件
            if {[file exists $client_result_path]} {
                file delete $client_result_path
                puts "已删除 client_result_done 文件"
            } else {
                puts "client_result_done 文件不存在，无需删除"
            }
            # 写server_result_done文件，告诉AI工具脚本执行完成
            set server_result_path [file join $target_dir "server_result_done"]
            if {[file exists $server_result_path]} {
                puts "已存在 server_result_done 文件"
            } else {
                puts "创建 server_result_done 文件"
                set f [open $server_result_path w]
                puts $f "done"
                close $f
            }
        }
        # 检查如果有command_reader_stop文件，则退出
        set command_reader_stop_path [file join $target_dir "command_reader_stop"]
        if {[file exists $command_reader_stop_path]} {
            puts "检测到 command_reader_stop 文件"
            break
        }
        # 短暂休眠，避免过度占用CPU
        after 10  ;# 休眠1秒
    }
}

# 启动监控
monitor_client_result
