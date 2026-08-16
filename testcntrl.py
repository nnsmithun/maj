from os_ken.base import app_manager

from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    CONFIG_DISPATCHER,
    MAIN_DISPATCHER,
    DEAD_DISPATCHER,
    set_ev_cls
)

from os_ken.ofproto import ofproto_v1_3

from os_ken.lib import hub

from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken.lib.packet import ether_types
from os_ken.lib.packet import ipv4
from os_ken.lib.packet import tcp
from os_ken.lib.packet import udp
from os_ken.lib.packet import icmp

import csv
import json
import os
import time


class MAJORTestController(app_manager.OSKenApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def __init__(self, *args, **kwargs):

        super(MAJORTestController, self).__init__(*args, **kwargs)

        # MAC address -> switch port
        self.mac_to_port = {}

        # Connected datapaths
        self.datapaths = {}

        # Statistics polling interval
        self.stats_interval = 5

        # --------------------------------------------------
        # Dataset files
        # --------------------------------------------------

        self.base_dir = "/home/mininet/maj"

        self.state_file = os.path.join(
            self.base_dir,
            "experiment_state.json"
        )

        self.dataset_dir = os.path.join(
            self.base_dir,
            "dataset"
        )

        self.csv_file = os.path.join(
            self.dataset_dir,
            "flow_stats.csv"
        )

        os.makedirs(
            self.dataset_dir,
            exist_ok=True
        )

        self._prepare_csv()

        # Start statistics polling thread
        self.monitor_thread = hub.spawn(
            self._monitor
        )

    # --------------------------------------------------
    # Experiment state
    # --------------------------------------------------

    def _get_experiment_state(self):

        default_state = {
            "experiment_id": "UNASSIGNED",
            "label": "UNLABELED"
        }

        try:

            if not os.path.exists(
                self.state_file
            ):
                return default_state

            with open(
                self.state_file,
                "r"
            ) as f:

                state = json.load(f)

            return {
                "experiment_id": state.get(
                    "experiment_id",
                    "UNASSIGNED"
                ),
                "label": state.get(
                    "label",
                    "UNLABELED"
                )
            }

        except Exception as e:

            self.logger.warning(
                "Could not read experiment state: %s",
                e
            )

            return default_state

    # --------------------------------------------------
    # CSV Initialization
    # --------------------------------------------------

    def _prepare_csv(self):

        file_exists = os.path.exists(
            self.csv_file
        )

        if not file_exists:

            with open(
                self.csv_file,
                "w",
                newline=""
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    "timestamp",
                    "experiment_id",
                    "label",

                    "datapath_id",
                    "table_id",
                    "priority",

                    "in_port",
                    "out_port",

                    "eth_src",
                    "eth_dst",
                    "eth_type",

                    "ip_src",
                    "ip_dst",
                    "ip_proto",

                    "src_port",
                    "dst_port",

                    "packet_count",
                    "byte_count",

                    "duration_sec",
                    "duration_nsec"
                ])

    # --------------------------------------------------
    # Switch Connected
    # --------------------------------------------------

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath

        self.datapaths[
            datapath.id
        ] = datapath

        self.logger.info(
            "Switch connected - DPID: %s",
            datapath.id
        )

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # --------------------------------------------------
        # Table-miss rule
        # --------------------------------------------------

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(
            datapath,
            priority=0,
            match=match,
            actions=actions
        )

    # --------------------------------------------------
    # Add Flow
    # --------------------------------------------------

    def add_flow(
        self,
        datapath,
        priority,
        match,
        actions,
        buffer_id=None
    ):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        if buffer_id is not None:

            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=instructions
            )

        else:

            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=instructions
            )

        datapath.send_msg(mod)

    # --------------------------------------------------
    # Packet-In
    # --------------------------------------------------

    @set_ev_cls(
        ofp_event.EventOFPPacketIn,
        MAIN_DISPATCHER
    )
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        in_port = msg.match[
            "in_port"
        ]

        pkt = packet.Packet(
            msg.data
        )

        eth = pkt.get_protocol(
            ethernet.ethernet
        )

        if eth is None:
            return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id

        # --------------------------------------------------
        # MAC learning
        # --------------------------------------------------

        self.mac_to_port.setdefault(
            dpid,
            {}
        )

        self.mac_to_port[
            dpid
        ][src] = in_port

        # --------------------------------------------------
        # Determine output port
        # --------------------------------------------------

        if dst in self.mac_to_port[
            dpid
        ]:

            out_port = self.mac_to_port[
                dpid
            ][dst]

        else:

            out_port = (
                ofproto.OFPP_FLOOD
            )

        actions = [
            parser.OFPActionOutput(
                out_port
            )
        ]

        # --------------------------------------------------
        # Build informative flow match
        # --------------------------------------------------

        match = self._build_match(
            parser,
            in_port,
            pkt,
            src,
            dst
        )

        # --------------------------------------------------
        # Install flow if destination known
        # --------------------------------------------------

        if out_port != ofproto.OFPP_FLOOD:

            self.add_flow(
                datapath,
                priority=10,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id
            )

            if (
                msg.buffer_id
                != ofproto.OFP_NO_BUFFER
            ):

                return

        # --------------------------------------------------
        # Packet-Out
        # --------------------------------------------------

        data = None

        if (
            msg.buffer_id
            == ofproto.OFP_NO_BUFFER
        ):

            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )

        datapath.send_msg(out)

    # --------------------------------------------------
    # Build Flow Match
    # --------------------------------------------------

    def _build_match(
        self,
        parser,
        in_port,
        pkt,
        src,
        dst
    ):

        ip_pkt = pkt.get_protocol(
            ipv4.ipv4
        )

        if ip_pkt is not None:

            proto = ip_pkt.proto

            # ----------------------------------------------
            # TCP
            # ----------------------------------------------

            tcp_pkt = pkt.get_protocol(
                tcp.tcp
            )

            if tcp_pkt is not None:

                return parser.OFPMatch(
                    in_port=in_port,
                    eth_src=src,
                    eth_dst=dst,
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_src=ip_pkt.src,
                    ipv4_dst=ip_pkt.dst,
                    ip_proto=proto,
                    tcp_src=tcp_pkt.src_port,
                    tcp_dst=tcp_pkt.dst_port
                )

            # ----------------------------------------------
            # UDP
            # ----------------------------------------------

            udp_pkt = pkt.get_protocol(
                udp.udp
            )

            if udp_pkt is not None:

                return parser.OFPMatch(
                    in_port=in_port,
                    eth_src=src,
                    eth_dst=dst,
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_src=ip_pkt.src,
                    ipv4_dst=ip_pkt.dst,
                    ip_proto=proto,
                    udp_src=udp_pkt.src_port,
                    udp_dst=udp_pkt.dst_port
                )

            # ----------------------------------------------
            # ICMP
            # ----------------------------------------------

            icmp_pkt = pkt.get_protocol(
                icmp.icmp
            )

            if icmp_pkt is not None:

                return parser.OFPMatch(
                    in_port=in_port,
                    eth_src=src,
                    eth_dst=dst,
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_src=ip_pkt.src,
                    ipv4_dst=ip_pkt.dst,
                    ip_proto=proto
                )

            # ----------------------------------------------
            # Other IPv4
            # ----------------------------------------------

            return parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=ip_pkt.src,
                ipv4_dst=ip_pkt.dst,
                ip_proto=proto
            )

        # --------------------------------------------------
        # Non-IPv4
        # --------------------------------------------------

        return parser.OFPMatch(
            in_port=in_port,
            eth_src=src,
            eth_dst=dst
        )

    # --------------------------------------------------
    # Monitor Thread
    # --------------------------------------------------

    def _monitor(self):

        while True:

            for datapath in list(
                self.datapaths.values()
            ):

                self._request_flow_stats(
                    datapath
                )

            hub.sleep(
                self.stats_interval
            )

    # --------------------------------------------------
    # Request Flow Statistics
    # --------------------------------------------------

    def _request_flow_stats(
        self,
        datapath
    ):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()

        req = parser.OFPFlowStatsRequest(
            datapath=datapath,
            table_id=ofproto.OFPTT_ALL,
            out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY,
            cookie=0,
            cookie_mask=0,
            match=match
        )

        datapath.send_msg(req)

    # --------------------------------------------------
    # Flow Statistics Reply
    # --------------------------------------------------

    @set_ev_cls(
        ofp_event.EventOFPFlowStatsReply,
        MAIN_DISPATCHER
    )
    def flow_stats_reply_handler(
        self,
        ev
    ):

        timestamp = time.time()

        datapath = ev.msg.datapath

        # Read label ONCE for this statistics reply.
        state = self._get_experiment_state()

        experiment_id = state[
            "experiment_id"
        ]

        label = state[
            "label"
        ]

        for stat in ev.msg.body:

            # Ignore table-miss
            if stat.priority == 0:
                continue

            match = stat.match

            # --------------------------------------------------
            # Match fields
            # --------------------------------------------------

            in_port = match.get(
                "in_port",
                ""
            )

            eth_src = match.get(
                "eth_src",
                ""
            )

            eth_dst = match.get(
                "eth_dst",
                ""
            )

            eth_type = match.get(
                "eth_type",
                ""
            )

            ip_src = match.get(
                "ipv4_src",
                ""
            )

            ip_dst = match.get(
                "ipv4_dst",
                ""
            )

            ip_proto = match.get(
                "ip_proto",
                ""
            )

            src_port = ""
            dst_port = ""

            # TCP
            if "tcp_src" in match:

                src_port = match.get(
                    "tcp_src",
                    ""
                )

                dst_port = match.get(
                    "tcp_dst",
                    ""
                )

            # UDP
            elif "udp_src" in match:

                src_port = match.get(
                    "udp_src",
                    ""
                )

                dst_port = match.get(
                    "udp_dst",
                    ""
                )

            # --------------------------------------------------
            # Output port
            # --------------------------------------------------

            out_port = ""

            if stat.instructions:

                for instruction in stat.instructions:

                    if not hasattr(
                        instruction,
                        "actions"
                    ):
                        continue

                    for action in instruction.actions:

                        if hasattr(
                            action,
                            "port"
                        ):

                            out_port = (
                                action.port
                            )

            # --------------------------------------------------
            # Write CSV
            # --------------------------------------------------

            with open(
                self.csv_file,
                "a",
                newline=""
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    timestamp,
                    experiment_id,
                    label,

                    datapath.id,
                    stat.table_id,
                    stat.priority,

                    in_port,
                    out_port,

                    eth_src,
                    eth_dst,
                    eth_type,

                    ip_src,
                    ip_dst,
                    ip_proto,

                    src_port,
                    dst_port,

                    stat.packet_count,
                    stat.byte_count,

                    stat.duration_sec,
                    stat.duration_nsec
                ])

            # --------------------------------------------------
            # Console output
            # --------------------------------------------------

            self.logger.info(
                "FLOW | "
                "EXP=%s "
                "LABEL=%s "
                "DPID=%s "
                "IN=%s "
                "OUT=%s "
                "SRC=%s "
                "DST=%s "
                "PROTO=%s "
                "SPORT=%s "
                "DPORT=%s "
                "PACKETS=%s "
                "BYTES=%s "
                "DURATION=%ss",

                experiment_id,
                label,

                datapath.id,
                in_port,
                out_port,

                ip_src,
                ip_dst,
                ip_proto,

                src_port,
                dst_port,

                stat.packet_count,
                stat.byte_count,
                stat.duration_sec
            )

    # --------------------------------------------------
    # Switch Disconnect
    # --------------------------------------------------

    @set_ev_cls(
        ofp_event.EventOFPStateChange,
        [MAIN_DISPATCHER, CONFIG_DISPATCHER]
    )
    def state_change_handler(
        self,
        ev
    ):

        datapath = ev.datapath

        if ev.state == MAIN_DISPATCHER:

            if datapath.id not in self.datapaths:

                self.datapaths[
                    datapath.id
                ] = datapath

                self.logger.info(
                    "Datapath registered: %s",
                    datapath.id
                )

        elif ev.state == DEAD_DISPATCHER:

            if datapath.id in self.datapaths:

                del self.datapaths[
                    datapath.id
                ]

                self.logger.info(
                    "Datapath removed: %s",
                    datapath.id
                )