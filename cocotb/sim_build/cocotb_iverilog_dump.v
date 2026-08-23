module cocotb_iverilog_dump();
initial begin
    string dumpfile_path;    if ($value$plusargs("dumpfile_path=%s", dumpfile_path)) begin
        $dumpfile(dumpfile_path);
    end else begin
        $dumpfile("/foss/designs/convChip_chipaton/cocotb/sim_build/chip_top.fst");
    end
    $dumpvars(0, chip_top);
end
endmodule
