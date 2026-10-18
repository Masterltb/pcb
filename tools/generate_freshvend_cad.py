#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreshVend - Automated Fruit Vending Machine 3D CAD Generator
Generates full 3D assembly in FreeCAD:
- Frame (800 x 600 x 800 mm)
- 2 Vertical Dispensing Columns (170 mm fruit bowl stack)
- Dual-Tier Iris Aperture Escapement Mechanisms (Upper & Lower Iris per column)
- MG996R Servos and Linkages
- Active 38kHz IR Optical Drop Detection Gates
- FV-CTRL_RevA Mainboard (100x100mm) & 12V 40A Industrial Power Supply
- Dispensing Chute & Customer Retrieval Compartment
- STEP export, STL printable parts, and FreeCAD Project (.FCStd)
"""

import sys
import os
import math

try:
    import FreeCAD
    import Part
    from FreeCAD import Base, Vector
except ImportError as e:
    print(f"Error importing FreeCAD: {e}")
    sys.exit(1)

def create_freshvend_assembly():
    print("Creating FreeCAD Document 'FreshVend_Machine_3D'...")
    doc = FreeCAD.newDocument("FreshVend_Machine_3D")
    
    # -------------------------------------------------------------
    # 1. HELPER FUNCTIONS
    # -------------------------------------------------------------
    def add_part(shape, name, group=None):
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        if group:
            group.addObject(obj)
        return obj

    def make_beam(x1, y1, z1, x2, y2, z2, size=30.0):
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        bx = size if dx == 0 else abs(dx)
        by = size if dy == 0 else abs(dy)
        bz = size if dz == 0 else abs(dz)
        box = Part.makeBox(bx, by, bz)
        box.translate(Vector(min(x1, x2), min(y1, y2), min(z1, z2)))
        return box

    def make_hollow_cyl(r_out, r_in, h, pos, axis=Vector(0,0,1)):
        c_out = Part.makeCylinder(r_out, h, pos, axis)
        c_in = Part.makeCylinder(r_in, h, pos, axis)
        return c_out.cut(c_in)

    # -------------------------------------------------------------
    # 2. MACHINE FRAME (800 x 600 x 800 mm)
    # -------------------------------------------------------------
    print("Building Frame (800 x 600 x 800 mm)...")
    grp_frame = doc.addObject("App::DocumentObjectGroup", "Frame_Structure")
    
    W = 800.0
    D = 600.0
    H = 800.0
    prof = 30.0
    
    # 4 Vertical corner posts
    p1 = make_beam(0, 0, 0, 0, 0, H, prof)
    p2 = make_beam(W - prof, 0, 0, W - prof, 0, H, prof)
    p3 = make_beam(0, D - prof, 0, 0, D - prof, H, prof)
    p4 = make_beam(W - prof, D - prof, 0, W - prof, D - prof, H, prof)
    frame_verticals = p1.fuse(p2).fuse(p3).fuse(p4)
    add_part(frame_verticals, "Frame_Corner_Posts", grp_frame)
    
    # Bottom perimeter beams
    b_bot_front = make_beam(prof, 0, 0, W - prof, 0, prof, prof)
    b_bot_back = make_beam(prof, D - prof, 0, W - prof, D - prof, prof, prof)
    b_bot_left = make_beam(0, prof, 0, 0, D - prof, prof, prof)
    b_bot_right = make_beam(W - prof, prof, 0, W - prof, D - prof, prof, prof)
    frame_bottom = b_bot_front.fuse(b_bot_back).fuse(b_bot_left).fuse(b_bot_right)
    add_part(frame_bottom, "Frame_Bottom_Rails", grp_frame)
    
    # Top perimeter beams
    b_top_front = make_beam(prof, 0, H - prof, W - prof, 0, H, prof)
    b_top_back = make_beam(prof, D - prof, H - prof, W - prof, D - prof, H, prof)
    b_top_left = make_beam(0, prof, H - prof, 0, D - prof, H, prof)
    b_top_right = make_beam(W - prof, prof, H - prof, W - prof, D - prof, H, prof)
    frame_top = b_top_front.fuse(b_top_back).fuse(b_top_left).fuse(b_top_right)
    add_part(frame_top, "Frame_Top_Rails", grp_frame)
    
    # Middle crossbeams supporting Iris floor at Z = 180mm
    mid_z = 180.0
    cb1 = make_beam(prof, 160.0, mid_z, W - prof, 160.0, mid_z + prof, prof)
    cb2 = make_beam(prof, 410.0, mid_z, W - prof, 410.0, mid_z + prof, prof)
    add_part(cb1.fuse(cb2), "Iris_Support_Crossbeams", grp_frame)

    # Base mounting shelf plate
    shelf = Part.makeBox(W - 2*prof, D - 2*prof, 3.0)
    shelf.translate(Vector(prof, prof, 10.0))
    # Cut holes for bottom drops
    hole1 = Part.makeCylinder(100.0, 10.0, Vector(260.0, 300.0, 5.0))
    hole2 = Part.makeCylinder(100.0, 10.0, Vector(540.0, 300.0, 5.0))
    shelf = shelf.cut(hole1).cut(hole2)
    add_part(shelf, "Bottom_Mounting_Baseplate", grp_frame)

    # -------------------------------------------------------------
    # 3. FRUIT BOWL 3D MODEL GENERATOR (170mm rim, 60mm height, 850ml)
    # -------------------------------------------------------------
    print("Defining Fruit Bowl Geometry (170mm Dia, 60mm H)...")
    def make_bowl(center_x, center_y, base_z):
        # Outer cone + flange rim
        # Rim flange: OD = 170 mm (R=85), ID = 160 mm (R=80), height 2.5 mm
        rim_outer = Part.makeCylinder(85.0, 2.5, Vector(center_x, center_y, base_z + 57.5))
        # Body cone: R_top = 80, R_bot = 60, height = 57.5
        body_outer = Part.makeCone(60.0, 80.0, 57.5, Vector(center_x, center_y, base_z))
        solid_bowl = body_outer.fuse(rim_outer)
        
        # Hollow inner cut (wall thickness 1.5 mm)
        inner_cone = Part.makeCone(58.5, 78.5, 59.0, Vector(center_x, center_y, base_z + 1.5))
        hollow_bowl = solid_bowl.cut(inner_cone)
        return hollow_bowl

    # -------------------------------------------------------------
    # 4. IRIS APERTURE MECHANISM GENERATOR (Model 5122 concept)
    # -------------------------------------------------------------
    print("Building Dual-Tier Iris Mechanisms...")
    def make_iris_assembly(name_prefix, cx, cy, cz, state="closed", parent_group=None):
        grp_iris = doc.addObject("App::DocumentObjectGroup", f"{name_prefix}_Group")
        if parent_group:
            parent_group.addObject(grp_iris)

        # A. Stator Baseplate: 240 x 240 x 5 mm with 185 mm center hole
        stator_plate = Part.makeBox(240.0, 240.0, 5.0)
        stator_plate.translate(Vector(cx - 120.0, cy - 120.0, cz))
        center_hole = Part.makeCylinder(92.5, 10.0, Vector(cx, cy, cz - 2.0))
        stator = stator_plate.cut(center_hole)
        
        # Stator blade pivot sockets (6 sockets at R = 105 mm)
        R_pivot = 105.0
        for i in range(6):
            ang = math.radians(i * 60.0)
            px = cx + R_pivot * math.cos(ang)
            py = cy + R_pivot * math.sin(ang)
            sock = Part.makeCylinder(2.5, 3.0, Vector(px, py, cz + 2.0))
            stator = stator.cut(sock)
        add_part(stator, f"{name_prefix}_Stator_Base", grp_iris)

        # B. Rotor Drive Ring (OD 230, ID 192, thickness 3.5 mm) at cz + 5.0
        rotor_ring = make_hollow_cyl(115.0, 96.0, 3.5, Vector(cx, cy, cz + 5.0))
        # Drive lever arm extending towards servo
        arm = Part.makeBox(35.0, 16.0, 3.5)
        arm.translate(Vector(cx + 95.0, cy - 8.0, cz + 5.0))
        rotor = rotor_ring.fuse(arm)
        add_part(rotor, f"{name_prefix}_Drive_Rotor_Ring", grp_iris)

        # C. 6 Iris Blades (Leaves)
        # In OPEN state: aperture R = 92.5 mm (Dia 185 mm > 170 mm bowl)
        # In CLOSED state: aperture R = 67.5 mm (Dia 135 mm, clamps under bowl rim)
        blade_shapes = []
        angle_swing = 0.0 if state == "open" else 28.0 # degrees pivot rotation
        
        for i in range(6):
            base_ang = i * 60.0
            # Pivot center on stator
            ang_rad = math.radians(base_ang)
            px = cx + R_pivot * math.cos(ang_rad)
            py = cy + R_pivot * math.sin(ang_rad)
            
            # Create a curved blade plate
            # Main crescent body: outer cylinder cut by offset inner cylinder
            c_blade_out = Part.makeCylinder(95.0, 2.5, Vector(cx, cy, cz + 5.5))
            
            # Aperture cut determines iris opening
            aperture_r = 92.5 if state == "open" else 67.5
            # Offset center for progressive blade overlap
            off_ang = math.radians(base_ang + 30.0 + (angle_swing if state == "closed" else 0.0))
            # Slice sector for blade
            wedge = Part.makeBox(130.0, 90.0, 3.0)
            wedge.translate(Vector(cx, cy, cz + 5.2))
            wedge.rotate(Vector(cx, cy, cz + 5.2), Vector(0, 0, 1), base_ang + angle_swing)
            
            blade_seg = c_blade_out.common(wedge)
            # Cut center aperture
            blade_cut = Part.makeCylinder(aperture_r, 4.0, Vector(cx, cy, cz + 5.0))
            blade_solid = blade_seg.cut(blade_cut)
            
            # Add pivot pin
            pin = Part.makeCylinder(2.2, 3.0, Vector(px, py, cz + 3.0))
            blade_complete = blade_solid.fuse(pin)
            blade_shapes.append(blade_complete)
            
        # Combine blades for visual performance or keep individual
        blades_fused = blade_shapes[0]
        for b in blade_shapes[1:]:
            blades_fused = blades_fused.fuse(b)
        add_part(blades_fused, f"{name_prefix}_Blades_x6_{state.upper()}", grp_iris)

        # D. Retaining Cover Ring (OD 230, ID 185, thickness 2.5 mm) at cz + 9.0
        cover = make_hollow_cyl(115.0, 92.5, 2.5, Vector(cx, cy, cz + 9.0))
        add_part(cover, f"{name_prefix}_Retaining_Cover", grp_iris)

        # E. MG996R Servo Motor & Mounting Bracket
        # Servo body: 40.7 x 19.7 x 36 mm, tab flange 54 x 19.7 mm
        sx = cx + 135.0
        sy = cy - 10.0
        sz = cz + 2.0
        
        # Servo bracket
        bracket = Part.makeBox(25.0, 60.0, 35.0)
        bracket.translate(Vector(sx - 5.0, sy - 15.0, sz))
        bracket_cut = Part.makeBox(22.0, 42.0, 35.0)
        bracket_cut.translate(Vector(sx - 3.0, sy - 6.0, sz + 2.0))
        bracket = bracket.cut(bracket_cut)
        add_part(bracket, f"{name_prefix}_Servo_Bracket", grp_iris)
        
        # Servo body
        servo_main = Part.makeBox(20.0, 40.7, 36.0)
        servo_main.translate(Vector(sx, sy - 5.0, sz + 2.0))
        # Mounting flanges
        flange = Part.makeBox(20.0, 54.0, 3.0)
        flange.translate(Vector(sx, sy - 11.5, sz + 22.0))
        # Output gear tower
        gear_tower = Part.makeCylinder(6.0, 7.0, Vector(sx + 10.0, sy + 7.0, sz + 38.0))
        # Servo horn / arm
        horn = Part.makeBox(6.0, 24.0, 2.5)
        horn.translate(Vector(sx + 7.0, sy - 5.0, sz + 43.0))
        servo_assembly = servo_main.fuse(flange).fuse(gear_tower).fuse(horn)
        add_part(servo_assembly, f"{name_prefix}_MG996R_Servo", grp_iris)

        # Linkage rod connecting servo horn to rotor arm
        linkage = Part.makeCylinder(1.5, 28.0, Vector(sx + 10.0, sy + 7.0, sz + 12.0), Vector(-1, 0, 0))
        add_part(linkage, f"{name_prefix}_Linkage_Pushrod", grp_iris)

        return grp_iris

    # -------------------------------------------------------------
    # 5. COLUMN 1 & COLUMN 2 SUBASSEMBLIES
    # -------------------------------------------------------------
    print("Assembling Column 1 (X=260mm) and Column 2 (X=540mm)...")
    columns_config = [
        {"name": "Col1", "cx": 260.0, "cy": 300.0},
        {"name": "Col2", "cx": 540.0, "cy": 300.0}
    ]
    
    for col in columns_config:
        cname = col["name"]
        cx = col["cx"]
        cy = col["cy"]
        grp_col = doc.addObject("App::DocumentObjectGroup", f"{cname}_Assembly")
        
        # A. Guide Rods (6 vertical stainless steel rods Ø8mm at R=92.5mm)
        # Inner clear aperture = 185 mm, fits 170 mm bowl with 7.5 mm clearance
        guide_rods = []
        for i in range(6):
            ang = math.radians(i * 60.0 + 30.0)
            gx = cx + 92.0 * math.cos(ang)
            gy = cy + 92.0 * math.sin(ang)
            rod = Part.makeCylinder(4.0, 490.0, Vector(gx, gy, 275.0))
            guide_rods.append(rod)
        fused_rods = guide_rods[0]
        for r in guide_rods[1:]:
            fused_rods = fused_rods.fuse(r)
        add_part(fused_rods, f"{cname}_Vertical_Guide_Rods", grp_col)

        # B. Top Funnel Loading Ring at Z = 765 mm
        funnel_outer = Part.makeCone(95.0, 110.0, 30.0, Vector(cx, cy, 765.0))
        funnel_inner = Part.makeCone(91.0, 106.0, 31.0, Vector(cx, cy, 764.5))
        top_funnel = funnel_outer.cut(funnel_inner)
        add_part(top_funnel, f"{cname}_Top_Restock_Funnel", grp_col)

        # C. Lower Iris (Mechanism 1 - DƯỚI) at Z = 200 mm
        # In Standby/Idle: Lower Iris is CLOSED (holding bottom bowl)
        make_iris_assembly(f"{cname}_Lower_Iris_Mech1", cx, cy, 200.0, state="closed", parent_group=grp_col)

        # D. Upper Iris (Mechanism 2 - TRÊN) at Z = 260 mm (offset 60mm = bowl height)
        # In Standby/Idle: Upper Iris is OPEN
        make_iris_assembly(f"{cname}_Upper_Iris_Mech2", cx, cy, 260.0, state="open", parent_group=grp_col)

        # E. Stack of 5 Fruit Bowls (850ml, 170mm rim)
        grp_bowls = doc.addObject("App::DocumentObjectGroup", f"{cname}_Fruit_Bowls_Stack")
        grp_col.addObject(grp_bowls)
        
        # Bowl 1: Bottom bowl resting on Lower Iris (Z = 200 mm)
        b1 = make_bowl(cx, cy, 200.0)
        add_part(b1, f"{cname}_Bowl_1_Bottom", grp_bowls)
        
        # Bowl 2: Second bowl positioned at Z = 260 mm (grip line for Upper Iris)
        b2 = make_bowl(cx, cy, 260.0)
        add_part(b2, f"{cname}_Bowl_2_UpperGate", grp_bowls)

        # Bowls 3, 4, 5: Stacked upward in column
        b3 = make_bowl(cx, cy, 320.0)
        add_part(b3, f"{cname}_Bowl_3", grp_bowls)
        b4 = make_bowl(cx, cy, 380.0)
        add_part(b4, f"{cname}_Bowl_4", grp_bowls)
        b5 = make_bowl(cx, cy, 440.0)
        add_part(b5, f"{cname}_Bowl_5", grp_bowls)

        # F. Active 38kHz IR Optical Drop Detection Gate at Z = 120 mm
        grp_ir = doc.addObject("App::DocumentObjectGroup", f"{cname}_IR_Drop_Sensor")
        grp_col.addObject(grp_ir)
        
        # IR TX LED (940nm) on Left
        tx_housing = Part.makeBox(20.0, 20.0, 25.0)
        tx_housing.translate(Vector(cx - 125.0, cy - 10.0, 110.0))
        tx_led = Part.makeCylinder(2.5, 8.0, Vector(cx - 105.0, cy, 122.5), Vector(1, 0, 0))
        ir_tx = tx_housing.fuse(tx_led)
        add_part(ir_tx, f"{cname}_IR_TX_Transmitter", grp_ir)

        # IR RX Daughterboard (FV-IR-RX_RevA) on Right
        rx_pcb = Part.makeBox(2.0, 35.0, 25.0)
        rx_pcb.translate(Vector(cx + 115.0, cy - 17.5, 110.0))
        tsop_body = Part.makeBox(5.0, 6.0, 7.0)
        tsop_body.translate(Vector(cx + 110.0, cy - 3.0, 119.0))
        ir_rx = rx_pcb.fuse(tsop_body)
        add_part(ir_rx, f"{cname}_FV_IR_RX_Receiver_Board", grp_ir)

        # Optical beam path visualization line
        beam = Part.makeCylinder(0.8, 215.0, Vector(cx - 105.0, cy, 122.5), Vector(1, 0, 0))
        add_part(beam, f"{cname}_IR_Optical_Beam_Line", grp_ir)

    # -------------------------------------------------------------
    # 6. DISPENSING CHUTE & COLLECTION HATCH
    # -------------------------------------------------------------
    print("Building Dispensing Chute & Collection Tray...")
    grp_chute = doc.addObject("App::DocumentObjectGroup", "Dispensing_Chute_Assembly")
    
    # Dual-hopper ramp sloping forward 30 degrees toward front Y = 0
    # Slope from Z = 160 mm down to Z = 35 mm at front retrieval window
    chute_plate = Part.makeBox(680.0, 280.0, 4.0)
    chute_plate.translate(Vector(60.0, 50.0, 35.0))
    # Rotate plate around X-axis for slope
    chute_plate.rotate(Vector(60.0, 50.0, 35.0), Vector(1, 0, 0), 22.0)
    add_part(chute_plate, "Chute_Slanted_Slide", grp_chute)
    
    # Side guard rails
    guard_l = Part.makeBox(4.0, 320.0, 80.0)
    guard_l.translate(Vector(56.0, 20.0, 35.0))
    guard_r = Part.makeBox(4.0, 320.0, 80.0)
    guard_r.translate(Vector(740.0, 20.0, 35.0))
    add_part(guard_l.fuse(guard_r), "Chute_Side_Guards", grp_chute)

    # Front retrieval door frame (340 x 140 mm at front face Y=0)
    door_frame = Part.makeBox(360.0, 15.0, 150.0)
    door_frame.translate(Vector(220.0, 0.0, 25.0))
    door_cut = Part.makeBox(330.0, 20.0, 125.0)
    door_cut.translate(Vector(235.0, -2.0, 38.0))
    door = door_frame.cut(door_cut)
    add_part(door, "Customer_Retrieval_Hatch_Door", grp_chute)

    # -------------------------------------------------------------
    # 7. ELECTRONICS & POWER SUBSYSTEM (FV-CTRL_RevA & 12V 40A PSU)
    # -------------------------------------------------------------
    print("Adding Control Mainboard (FV-CTRL_RevA) & 12V 40A PSU...")
    grp_elec = doc.addObject("App::DocumentObjectGroup", "Electronics_Subsystem")
    
    # A. FV-CTRL_RevA Mainboard (100 x 100 x 1.6 mm green PCB on right side)
    pcb_x = 765.0
    pcb_y = 250.0
    pcb_z = 380.0
    
    pcb_base = Part.makeBox(1.6, 100.0, 100.0)
    pcb_base.translate(Vector(pcb_x, pcb_y, pcb_z))
    
    # ESP32 DevKit 38-Pin model (28 x 54 x 6 mm)
    esp32 = Part.makeBox(6.0, 28.0, 54.0)
    esp32.translate(Vector(pcb_x - 6.0, pcb_y + 36.0, pcb_z + 23.0))
    # USB-C port facing bottom/edge
    usb = Part.makeBox(7.0, 9.0, 4.0)
    usb.translate(Vector(pcb_x - 7.0, pcb_y + 45.0, pcb_z + 19.0))
    
    # Dual XL4015 Buck Converter Modules (24 x 54 x 18 mm each)
    buck1 = Part.makeBox(18.0, 24.0, 54.0)
    buck1.translate(Vector(pcb_x - 18.0, pcb_y + 5.0, pcb_z + 5.0))
    buck2 = Part.makeBox(18.0, 24.0, 54.0)
    buck2.translate(Vector(pcb_x - 18.0, pcb_y + 5.0, pcb_z + 40.0))
    
    # MP1584EN 5V Buck Module (17 x 22 x 5 mm)
    buck_5v = Part.makeBox(6.0, 17.0, 22.0)
    buck_5v.translate(Vector(pcb_x - 6.0, pcb_y + 75.0, pcb_z + 70.0))
    
    # Bulk filter capacitors (2x Ø12.5mm x 25mm electrolytic caps 2200uF)
    cap1 = Part.makeCylinder(6.25, 25.0, Vector(pcb_x - 25.0, pcb_y + 15.0, pcb_z + 20.0), Vector(1, 0, 0))
    cap2 = Part.makeCylinder(6.25, 25.0, Vector(pcb_x - 25.0, pcb_y + 15.0, pcb_z + 55.0), Vector(1, 0, 0))
    
    # Screw terminal blocks & fuse holder
    terminal = Part.makeBox(12.0, 25.0, 15.0)
    terminal.translate(Vector(pcb_x - 12.0, pcb_y + 70.0, pcb_z + 10.0))
    
    fv_board = pcb_base.fuse(esp32).fuse(usb).fuse(buck1).fuse(buck2).fuse(buck_5v).fuse(cap1).fuse(cap2).fuse(terminal)
    add_part(fv_board, "FV_CTRL_RevA_Mainboard_Assembly", grp_elec)

    # B. Industrial 12V 40A Power Supply (215 x 115 x 50 mm)
    psu = Part.makeBox(215.0, 115.0, 50.0)
    psu.translate(Vector(290.0, 440.0, 15.0))
    add_part(psu, "Industrial_Power_Supply_12V_40A", grp_elec)

    # -------------------------------------------------------------
    # 8. RECOMPUTE & SAVE DOCUMENT
    # -------------------------------------------------------------
    print("Recomputing document...")
    doc.recompute()
    
    fcstd_path = os.path.abspath("cad/FreshVend_Machine_3D.FCStd")
    print(f"Saving FreeCAD Project to: {fcstd_path}")
    doc.saveAs(fcstd_path)
    
    # -------------------------------------------------------------
    # 9. EXPORT STEP FILE FOR CAD EXCHANGE
    # -------------------------------------------------------------
    step_path = os.path.abspath("cad/FreshVend_Machine_Assembly.step")
    print(f"Exporting complete STEP model to: {step_path}...")
    all_objs = doc.Objects
    Part.export([o for o in all_objs if hasattr(o, "Shape") and not o.Shape.isNull()], step_path)

    # -------------------------------------------------------------
    # 10. EXPORT INDIVIDUAL STL FILES FOR 3D PRINTING
    # -------------------------------------------------------------
    print("Exporting individual 3D printing STL components...")
    stl_parts = [
        ("cad/stl/Iris_Stator_Base.stl", "Col1_Lower_Iris_Mech1_Stator_Base"),
        ("cad/stl/Iris_Drive_Rotor_Ring.stl", "Col1_Lower_Iris_Mech1_Drive_Rotor_Ring"),
        ("cad/stl/Iris_Blades_x6_Closed.stl", "Col1_Lower_Iris_Mech1_Blades_x6_CLOSED"),
        ("cad/stl/Iris_Retaining_Cover.stl", "Col1_Lower_Iris_Mech1_Retaining_Cover"),
        ("cad/stl/Servo_MG996R_Bracket.stl", "Col1_Lower_Iris_Mech1_Servo_Bracket"),
        ("cad/stl/Fruit_Bowl_170mm.stl", "Col1_Bowl_1_Bottom"),
        ("cad/stl/Top_Restock_Funnel.stl", "Col1_Top_Restock_Funnel"),
    ]
    for stl_file, obj_name in stl_parts:
        target_obj = doc.getObject(obj_name)
        if target_obj:
            out_file = os.path.abspath(stl_file)
            target_obj.Shape.exportStl(out_file)
            print(f"  -> Exported: {stl_file}")

    print("\nSUCCESS! All CAD models generated.")
    return True

if __name__ == "__main__":
    create_freshvend_assembly()
