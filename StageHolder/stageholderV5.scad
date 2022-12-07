
difference(){
    union(){
        cube([80,60,5]);
        translate([0, 0, 0]) cube([80, 3, 10]);
        translate([0, 57, 0]) cube([80, 3, 10]);
        translate([0, 0, 0]) cube([5, 60, 10]);
        translate([37.5, 0, 0]) cube([5, 60, 10]);
        translate([75, 0, 0]) cube([5, 60, 10]);    
    }
    
    translate([10, 8,3]) cylinder(h = 6, r=2.6, center = true, $fn=20);
    translate([20, 18,3]) cylinder(h = 6, r=2.6, center = true, $fn=20);
    translate([70, 8,3]) cylinder(h = 6, r=2.6, center = true, $fn=20);
    translate([60, 18,3]) cylinder(h = 6, r=2.6, center = true, $fn=20);

    // for set screws
    translate([20, 60,7.5]) rotate([90,0,0]) cylinder(h = 10, d=2.26, center = true, $fn=20);
    translate([60, 60,7.5]) rotate([90,0,0]) cylinder(h = 10, d=2.26, center = true, $fn=20);


    translate([10, 50,3]) cube([5.2, 11, 6],center=true);
    translate([20, 40,3]) cube([5.2, 11, 6],center=true);
    translate([70, 50,3]) cube([5.2, 11, 6],center=true);
    translate([60, 40,3]) cube([5.2, 11, 6],center=true);
    
    translate([40, 30, 5.5]) cube([100, 3.2, 10],center=true); // cut between center pieces
}
