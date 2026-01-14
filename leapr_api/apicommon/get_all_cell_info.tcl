set cell_names [udm_get_prop [udm_get_obj -type cell] name]
#set cell_locs [llength [udm_get_prop [udm_get_obj -type cell] loc]]
set core_size [udm_get_prop [udm_get_obj -type floorplan] core_box_size]

#udm_get_prop [udm_get_obj -type net] name
# input_pin_count output_pin_count
# u_macc_top/macc[0].u_macc/n143
# cell name: u_macc_top/macc[1].u_macc/diff_reg_reg[3]
# 获取cell的pin: get_pins -of_objects [get_cells u_macc_top/macc[1].u_macc/diff_reg_reg[3]]
# 获取pin的地址: get_pin_by_full_name u_macc_top/macc[1].u_macc/diff_reg_reg[3]/QN
# 获取pin所属net的地址：get_pin_net [get_pin_by_full_name u_macc_top/macc[1].u_macc/diff_reg_reg[3]/QN]
# 获取pin所属net的名字：udm_get_prop [get_pin_net [get_pin_by_full_name u_macc_top/macc[1].u_macc/diff_reg_reg[3]/QN]] name
# 通过foreach方式遍历cell_names,获取每个cell的长、宽，获取每个cell的所有pin，每个pin所属的net, 保存到变量里，保存格式是：cell_name: [cell_width, cell_height, pin_name1, pin_name2, ..., pin_net1, pin_net2, ...]
#set cell_info_list [list]， 存一个结构: [{cell_name, width, height, {"pin1":[nets]}}]
# 获取net的driver pin: get_object_name  [get_attribute [get_nets u_macc_top/macc[1].u_macc/n165] driver_pins]
# 获取net的load pin: get_object_name  [get_attribute [get_nets u_macc_top/macc[1].u_macc/n165] load_pins]
set net_map {}
set server_result_txt [file join $api_dir "server_result.txt"]
set fp [open "${server_result_txt}" w]
puts $fp "=======design_info======="
puts $fp "core_size: $core_size"
puts $fp "=======cell_info======="
foreach cell_name $cell_names {
     # 如果cell_name包含WELLTAP,GATE等，则跳过
      if {[string first "WELLTAP" $cell_name] != -1} {
          incr no_pin_cell_num
          continue
      }
      if {[string first "ENDCAP" $cell_name] != -1} {
         incr no_pin_cell_num
         continue
      }
    set pin_count [get_attribute [get_cells $cell_name] pin_count]
    # 如果pin_count <=0，跳过
    if {$pin_count <= 0} {
        continue
    }
    set cell_width [udm_get_prop [get_obj_by_name $cell_name] bbox_x_length]
    set cell_height [udm_get_prop [get_obj_by_name $cell_name] bbox_y_length]
    set cell_orient [udm_get_prop [get_obj_by_name $cell_name] orient]
    set cell_place_status [udm_get_prop [get_obj_by_name $cell_name] place_status]
    set loc_x [udm_get_prop [get_obj_by_name $cell_name] loc_x]
    set loc_y [udm_get_prop [get_obj_by_name $cell_name] loc_y]
    set pin_names [get_object_name [get_pins -of_objects [get_cells $cell_name]]]
    set pin_names_str [join $pin_names "|"]
    foreach pin_name $pin_names {
        set pin_nets [udm_get_prop [get_pin_net [get_pin_by_full_name $pin_name]] name]
        if {![dict exists $net_map pin_nets]} {
            set load_pins [get_object_name  [get_attribute [get_nets $pin_nets] load_pins]]
            set driver_pins [get_object_name  [get_attribute [get_nets $pin_nets] driver_pins]]
            set load_pins_str [join $load_pins "|"]
            set driver_pins_str [join $driver_pins "|"]
            dict set net_map $pin_nets [list $load_pins_str $driver_pins_str]
        }
    }
    puts $fp $cell_name
    puts $fp "${cell_width},${cell_height},${cell_orient},${cell_place_status},${loc_x},${loc_y}"
    puts $fp $pin_names_str
}
puts $fp "=======net_info======="
set net_map_str ""
set first_item 1
dict for {net_name net_info} $net_map {
    set net_name_str [lindex $net_name 0]
    set load_pins [lindex $net_info 0]
    set driver_pins [lindex $net_info 1]
    puts $fp "${net_name_str},${load_pins},${driver_pins}"
}
puts $fp $net_map_str
# 将core_size和cell_info_list保存到server_result.txt文件中，cell_info_list中每个元素为一行
close $fp
