#!/usr/bin/env tclsh

# eda_server.tcl - TCL TCP Server for EDA Command Execution
#
# This script creates a TCP server that receives TCL commands/scripts from clients,
# executes them, and returns the results to the client.

package require Tcl 8.5

proc handle_client {channel client_address client_port} {
    puts "Client connected from $client_address:$client_port"
    
    # Set up error handling for the channel
    fconfigure $channel -buffering line -encoding utf-8
    
    # Send welcome message
    set welcome_msg "EDA Server Ready - Connected from $client_address:$client_port\n"
    catch {puts $channel $welcome_msg}
    
    # Process commands from the client
    while {[catch {gets $channel cmd} error] == 0} {
        if {[eof $channel]} {
            puts "Client $client_address:$client_port disconnected"
            close $channel
            return
        }
        
        if {$cmd eq "" || $cmd eq "exit" || $cmd eq "quit"} {
            puts "Client $client_address:$client_port requested disconnect"
            catch {puts $channel "Server closing connection"}
            catch {flush $channel}
            close $channel
            return
        }
        
        # Use a temporary channel to capture command output
        set temp_result [eval_cmd_with_output_capture $cmd]
        
        # Send response back to client
        if {[catch {puts $channel $temp_result} send_error]} {
            puts "Error sending response to client $client_address:$client_port: $send_error"
            close $channel
            return
        }
        
        # Flush the channel to ensure data is sent
        catch {flush $channel}
    }
    
    # Handle errors in gets command
    if {$error ne ""} {
        puts "Error reading from client $client_address:$client_port: $error"
    }
    
    # Close the channel
    catch {close $channel}
    puts "Closed connection to $client_address:$client_port"
}

proc start_server {port} {
    set server_socket [socket -server accept_connection -myaddr localhost $port]
    puts "EDA TCP Server listening on localhost:$port"
    
    # Keep the server running
    vwait forever
}

proc accept_connection {channel client_address client_port} {
    # Handle the new client connection in the background
    handle_client $channel $client_address $client_port
}

# Function to execute command and capture both result and puts output
proc eval_cmd_with_output_capture {cmd} {
    # Create a temporary buffer to capture output
    variable output_buffer ""
    set output_buffer ""
    
    # Temporarily redefine puts to capture its output
    rename ::puts ::original_puts
    proc ::puts {args} {
        variable output_buffer
        set argc [llength $args]
        
        # Handle different forms of puts
        if {$argc == 1} {
            # puts string
            append output_buffer [lindex $args 0]
            append output_buffer "\n"
        } elseif {$argc == 2} {
            set arg1 [lindex $args 0]
            set arg2 [lindex $args 1]
            if {$arg1 eq "-nonewline"} {
                # puts -nonewline string
                append output_buffer $arg2
            } elseif {[string is integer $arg1]} {
                # puts channelId string - this goes to the original puts
                return [uplevel ::original_puts $args]
            } else {
                # puts channel string
                append output_buffer $arg2
                append output_buffer "\n"
            }
        } elseif {$argc == 3} {
            set arg1 [lindex $args 0]
            if {$arg1 eq "-nonewline"} {
                # puts -nonewline channelId string - this goes to the original puts
                return [uplevel ::original_puts $args]
            }
        } else {
            # For other cases, use original puts
            return [uplevel ::original_puts $args]
        }
    }
    
    # Execute the command and capture its return value
    if {[catch {uplevel #0 $cmd} result]} {
        # Restore original puts
        rename ::puts ""
        rename ::original_puts ::puts
        return [list ERROR $result]
    } else {
        # Get the captured output
        variable output_buffer
        set captured_output $output_buffer
        
        # Restore original puts
        rename ::puts ""
        rename ::original_puts ::puts
        
        # Combine captured output with command result
        if {$captured_output eq ""} {
            return [list OK $result]
        } else {
            # If there's captured output, append command result if it's not empty
            if {$result eq ""} {
                return [list OK $captured_output]
            } else {
                return [list OK "$captured_output$result"]
            }
        }
    }
}

set port 5001
set run_background [expr {$argc == 2 && [lindex $argv 1] eq "background"}]

puts "Starting EDA Server on port $port..."

if {$run_background} {
    # Run server in background using after idle
    puts "Running server in background mode..."
    after idle [list start_server $port]
    
    # Keep the Tcl event loop running
    vwait forever
} else {
    # Run server in foreground
    start_server $port
}