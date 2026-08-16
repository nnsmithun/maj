#!/bin/bash

set -u

BASE="/home/mininet/maj"
BOTS_DIR="$BASE/bots"
STATE_FILE="$BASE/experiment_state.json"

# --------------------------------------------------
# Defaults
# --------------------------------------------------

DURATION=300

# Controlled default rates.
# Change these later during experiments if required.
SYN_RATE=20
UDP_RATE=50
HTTP_RATE=10
ICMP_RATE=5

LOW_RATE_INTERVAL=2
BURST_RATE=30
BURST_DURATION=3
BURST_IDLE=10


# --------------------------------------------------
# Check root
# --------------------------------------------------

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo."
    echo
    echo "Example:"
    echo "sudo ./run_experiment.sh SYN_FLOOD syn hbot1,hbot2,hbot3 300"
    exit 1
fi


# --------------------------------------------------
# Arguments
# --------------------------------------------------

LABEL="${1:-}"
TYPE="${2:-}"
BOT_LIST="${3:-}"
DURATION="${4:-$DURATION}"


if [ -z "$LABEL" ] || [ -z "$TYPE" ]; then

    echo
    echo "Usage:"
    echo
    echo "sudo ./run_experiment.sh LABEL TYPE BOT_LIST DURATION"
    echo
    echo "Examples:"
    echo
    echo "sudo ./run_experiment.sh SYN_FLOOD syn hbot1,hbot2,hbot3 300"
    echo "sudo ./run_experiment.sh UDP_FLOOD udp hbot1,hbot4,hbot7 300"
    echo "sudo ./run_experiment.sh HTTP_FLOOD http hbot2,hbot5 300"
    echo "sudo ./run_experiment.sh ICMP_FLOOD icmp hbot3,hbot6 300"
    echo "sudo ./run_experiment.sh LOW_RATE low_rate hbot1,hbot7 300"
    echo "sudo ./run_experiment.sh BURST burst hbot2,hbot3,hbot6 300"
    echo
    echo "BENIGN is run separately with:"
    echo "sudo ./run_experiment.sh BENIGN benign huser1,huser2 300"
    echo

    exit 1
fi


# --------------------------------------------------
# Validate duration
# --------------------------------------------------

if ! [[ "$DURATION" =~ ^[0-9]+$ ]]; then

    echo "Duration must be an integer."
    exit 1

fi


# --------------------------------------------------
# Generate experiment ID
# --------------------------------------------------

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

EXPERIMENT_ID="EXP_${TIMESTAMP}"


# --------------------------------------------------
# Validate traffic type
# --------------------------------------------------

case "$TYPE" in

    syn)
        SCRIPT="$BOTS_DIR/syn_bot.py"
        ;;

    udp)
        SCRIPT="$BOTS_DIR/udp_bot.py"
        ;;

    http)
        SCRIPT="$BOTS_DIR/http_bot.py"
        ;;

    icmp)
        SCRIPT="$BOTS_DIR/icmp_bot.py"
        ;;

    low_rate)
        SCRIPT="$BOTS_DIR/low_rate_bot.py"
        ;;

    burst)
        SCRIPT="$BOTS_DIR/burst_bot.py"
        ;;

    benign)
        SCRIPT="$BOTS_DIR/benign_client.py"
        ;;

    *)
        echo "Unknown traffic type: $TYPE"
        exit 1
        ;;

esac


# --------------------------------------------------
# Check script
# --------------------------------------------------

if [ ! -f "$SCRIPT" ]; then

    echo "ERROR: Generator not found:"
    echo "$SCRIPT"

    exit 1

fi


# --------------------------------------------------
# Write experiment state
# --------------------------------------------------

cat > "$STATE_FILE" <<EOF
{
    "experiment_id": "$EXPERIMENT_ID",
    "label": "$LABEL",
    "type": "$TYPE",
    "bots": "$BOT_LIST",
    "duration": $DURATION,
    "start_time": "$(date -Iseconds)"
}
EOF


echo
echo "=============================================="
echo "        MAJOR ONE EXPERIMENT"
echo "=============================================="
echo
echo "Experiment : $EXPERIMENT_ID"
echo "Label      : $LABEL"
echo "Type       : $TYPE"
echo "Hosts      : $BOT_LIST"
echo "Duration   : $DURATION seconds"
echo
echo "State file : $STATE_FILE"
echo
echo "=============================================="
echo


# --------------------------------------------------
# Find Mininet host PID
# --------------------------------------------------

get_host_pid() {

    HOST="$1"

    PID=$(pgrep -f \
        "bash --norc --noediting -is mininet:${HOST}" \
        | head -n 1)

    if [ -z "$PID" ]; then

        echo ""
        return 1

    fi

    echo "$PID"
}


# --------------------------------------------------
# Start one generator inside Mininet host
# --------------------------------------------------

start_generator() {

    HOST="$1"

    HOST_PID=$(get_host_pid "$HOST")

    if [ -z "$HOST_PID" ]; then

        echo
        echo "ERROR:"
        echo "Could not find Mininet host: $HOST"
        echo
        echo "Make sure topology2.py is running."
        echo
        exit 1

    fi

    echo "Starting $TYPE on $HOST (PID $HOST_PID)"


    case "$TYPE" in

        syn)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 3000 \
                --rate "$SYN_RATE" \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        udp)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 9999 \
                --rate "$UDP_RATE" \
                --size 512 \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        http)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 3000 \
                --rate "$HTTP_RATE" \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        icmp)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --rate "$ICMP_RATE" \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        low_rate)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 3000 \
                --interval "$LOW_RATE_INTERVAL" \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        burst)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 3000 \
                --burst-rate "$BURST_RATE" \
                --burst-duration "$BURST_DURATION" \
                --idle-duration "$BURST_IDLE" \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

        benign)

            mnexec -a "$HOST_PID" \
                python3 "$SCRIPT" \
                --target 10.0.0.100 \
                --port 3000 \
                --duration "$DURATION" \
                > "/tmp/${HOST}_traffic.log" 2>&1 &

            ;;

    esac
}


# --------------------------------------------------
# Start selected hosts
# --------------------------------------------------

IFS=',' read -ra HOSTS <<< "$BOT_LIST"


for HOST in "${HOSTS[@]}"; do

    HOST=$(echo "$HOST" | xargs)

    if [ -n "$HOST" ]; then

        start_generator "$HOST"

    fi

done


echo
echo "Traffic generation started."
echo
echo "Collecting for $DURATION seconds..."
echo


# --------------------------------------------------
# Wait
# --------------------------------------------------

sleep "$DURATION"


# --------------------------------------------------
# Stop traffic generators
# --------------------------------------------------

echo
echo "Stopping experiment traffic..."


for HOST in "${HOSTS[@]}"; do

    HOST=$(echo "$HOST" | xargs)

    if [ -z "$HOST" ]; then
        continue
    fi

    HOST_PID=$(get_host_pid "$HOST")

    if [ -n "$HOST_PID" ]; then

        # Stop only the generator belonging to this host.
        mnexec -a "$HOST_PID" \
            pkill -TERM -f "$SCRIPT" 2>/dev/null || true

    fi

done


# --------------------------------------------------
# Allow final statistics poll
# --------------------------------------------------

echo
echo "Waiting for final OpenFlow statistics..."
sleep 7


# --------------------------------------------------
# Mark experiment complete
# --------------------------------------------------

END_TIME=$(date -Iseconds)

cat > "$STATE_FILE" <<EOF
{
    "experiment_id": "$EXPERIMENT_ID",
    "label": "$LABEL",
    "type": "$TYPE",
    "bots": "$BOT_LIST",
    "duration": $DURATION,
    "start_time": "$(jq -r '.start_time' "$STATE_FILE" 2>/dev/null || echo "unknown")",
    "end_time": "$END_TIME",
    "status": "completed"
}
EOF


echo
echo "=============================================="
echo "        EXPERIMENT COMPLETE"
echo "=============================================="
echo
echo "Experiment : $EXPERIMENT_ID"
echo "Label      : $LABEL"
echo "Type       : $TYPE"
echo "Hosts      : $BOT_LIST"
echo "Duration   : $DURATION seconds"
echo
echo "Dataset:"
echo "$BASE/dataset/flow_stats.csv"
echo
echo "=============================================="