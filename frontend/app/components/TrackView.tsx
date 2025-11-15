"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Car } from "../types/race";

interface TrackViewProps {
  cars: Car[];
  trackLength: number;
}

export default function TrackView({
  cars,
  trackLength = 2370,
}: TrackViewProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || cars.length === 0) return;

    const svg = d3.select(svgRef.current);

    // Responsive dimensions
    const containerWidth = containerRef.current?.clientWidth || 900;
    const isMobile = containerWidth < 768;
    const width = isMobile
      ? Math.min(containerWidth - 20, 600)
      : Math.min(containerWidth - 20, 1600);
    const height = isMobile ? width * 0.75 : width * 0.6;
    const margin = isMobile ? 30 : 50;

    // Clear previous content
    svg.selectAll("*").remove();

    // Setup SVG with viewBox for responsive scaling
    svg
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", `0 0 900 400`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    // Plaksha E-Prix Circuit - Real Formula E track layout
    // Based on Plaksha International E-Prix Circuit (18 turns, 2.370 km)
    const centerX = 450; // Fixed for viewBox
    const centerY = 200; // Fixed for viewBox

    // Create Plaksha circuit path matching the attached image
    // Flowing street circuit with long straights and technical sections
    const trackPath = `
      M 200,300
      L 350,295
      Q 380,293 395,280
      L 410,265
      Q 420,250 430,245
      L 455,240
      Q 475,238 485,225
      L 495,210
      Q 500,195 515,190
      L 540,185
      Q 565,183 580,175
      L 605,160
      Q 625,150 640,145
      L 670,140
      Q 695,138 710,150
      L 725,165
      Q 735,180 745,195
      L 755,215
      Q 760,235 770,245
      L 785,260
      Q 800,270 810,265
      L 825,255
      Q 835,245 835,230
      L 835,210
      Q 835,190 825,180
      L 810,170
      Q 790,163 775,165
      L 750,170
      Q 730,175 720,190
      L 710,210
      Q 705,230 695,240
      L 675,255
      Q 655,265 640,275
      L 615,290
      Q 595,300 580,310
      L 555,325
      Q 535,335 520,345
      L 495,360
      Q 475,370 460,375
      L 435,380
      Q 410,383 395,390
      L 370,405
      Q 350,418 335,415
      L 315,410
      Q 295,405 285,395
      L 270,380
      Q 258,365 250,350
      L 240,330
      Q 235,315 225,310
      L 205,305
      Q 195,303 200,300
    `;

    // Draw track background (wider gray area)
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#1E3A4D")
      .attr("stroke-width", 32);

    // Draw track surface
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#0A1820")
      .attr("stroke-width", 26);

    // Draw track center line (solid thin line)
    svg
      .append("path")
      .attr("d", trackPath)
      .attr("fill", "none")
      .attr("stroke", "#142835")
      .attr("stroke-width", 2);

    // Get path element for calculations
    const pathElement = svg
      .append("path")
      .attr("d", trackPath)
      .node() as SVGPathElement;

    const pathLength = pathElement?.getTotalLength() || trackLength;

    // Start/Finish line
    const startPoint = pathElement?.getPointAtLength(0);
    if (startPoint) {
      // Start line
      svg
        .append("line")
        .attr("x1", startPoint.x - 13)
        .attr("y1", startPoint.y - 13)
        .attr("x2", startPoint.x - 13)
        .attr("y2", startPoint.y + 13)
        .attr("stroke", "#00FF9C")
        .attr("stroke-width", 3);

      svg
        .append("text")
        .attr("x", startPoint.x - 13)
        .attr("y", startPoint.y - 22)
        .attr("text-anchor", "middle")
        .attr("fill", "#00FF9C")
        .attr("font-size", "12px")
        .attr("font-weight", "bold")
        .text("START/FINISH");

      // Checkered pattern
      for (let i = 0; i < 6; i++) {
        svg
          .append("rect")
          .attr("x", startPoint.x - 15)
          .attr("y", startPoint.y - 13 + i * 4)
          .attr("width", 4)
          .attr("height", 4)
          .attr("fill", i % 2 === 0 ? "#FFFFFF" : "#041014");
      }
    }

    // Sector markers (3 sectors)
    const sector1End = 0.33;
    const sector2End = 0.66;

    // Sector 1 marker
    const s1Point = pathElement?.getPointAtLength(sector1End * pathLength);
    if (s1Point) {
      svg
        .append("line")
        .attr("x1", s1Point.x - 10)
        .attr("y1", s1Point.y - 10)
        .attr("x2", s1Point.x + 10)
        .attr("y2", s1Point.y + 10)
        .attr("stroke", "#FF3B3B")
        .attr("stroke-width", 3);

      svg
        .append("text")
        .attr("x", s1Point.x)
        .attr("y", s1Point.y - 15)
        .attr("text-anchor", "middle")
        .attr("fill", "#FF3B3B")
        .attr("font-size", "11px")
        .attr("font-weight", "bold")
        .text("SECTOR 1");
    }

    // Sector 2 marker
    const s2Point = pathElement?.getPointAtLength(sector2End * pathLength);
    if (s2Point) {
      svg
        .append("line")
        .attr("x1", s2Point.x - 10)
        .attr("y1", s2Point.y - 10)
        .attr("x2", s2Point.x + 10)
        .attr("y2", s2Point.y + 10)
        .attr("stroke", "#FFBB00")
        .attr("stroke-width", 3);

      svg
        .append("text")
        .attr("x", s2Point.x)
        .attr("y", s2Point.y + 25)
        .attr("text-anchor", "middle")
        .attr("fill", "#FFBB00")
        .attr("font-size", "11px")
        .attr("font-weight", "bold")
        .text("SECTOR 2");
    }

    // Attack Mode Zones (approximately 40% and 80% around track)
    const attackZone1Pos = 0.4;
    const attackZone2Pos = 0.8;

    const az1Point = pathElement?.getPointAtLength(attackZone1Pos * pathLength);
    if (az1Point) {
      svg
        .append("circle")
        .attr("cx", az1Point.x)
        .attr("cy", az1Point.y)
        .attr("r", 20)
        .attr("fill", "none")
        .attr("stroke", "#00E5FF")
        .attr("stroke-width", 3);

      svg
        .append("text")
        .attr("x", az1Point.x)
        .attr("y", az1Point.y + 4)
        .attr("text-anchor", "middle")
        .attr("fill", "#00E5FF")
        .attr("font-size", "14px")
        .attr("font-weight", "bold")
        .text("⚡");
    }

    const az2Point = pathElement?.getPointAtLength(attackZone2Pos * pathLength);
    if (az2Point) {
      svg
        .append("circle")
        .attr("cx", az2Point.x)
        .attr("cy", az2Point.y)
        .attr("r", 20)
        .attr("fill", "none")
        .attr("stroke", "#00E5FF")
        .attr("stroke-width", 3);

      svg
        .append("text")
        .attr("x", az2Point.x)
        .attr("y", az2Point.y + 4)
        .attr("text-anchor", "middle")
        .attr("fill", "#00E5FF")
        .attr("font-size", "14px")
        .attr("font-weight", "bold")
        .text("⚡");
    }

    // Sort cars by position
    const activeCars = cars.filter((car) => car.is_active);
    const sortedCars = [...activeCars].sort(
      (a, b) => b.total_distance - a.total_distance
    );

    // Define solid colors for cars
    const carColors = [
      "#FFBB00", // Leader - Yellow/Gold
      "#00E5FF", // 2nd - Cyan
      "#FF7A00", // 3rd - Orange
      "#00FF9C", // 4th - Green
      "#FF3B3B", // 5th - Red
      "#C9D1D9", // 6th - Light gray
      "#FFBB00", // Repeat colors
      "#00E5FF",
      "#FF7A00",
      "#00FF9C",
      "#FF3B3B",
      "#C9D1D9",
    ];

    // Draw cars on the track
    const carGroup = svg.append("g");

    sortedCars.forEach((car, index) => {
      // Calculate position on path
      const normalizedDistance = (car.lap_distance % trackLength) / trackLength;
      const distanceOnPath = normalizedDistance * pathLength;
      const point = pathElement?.getPointAtLength(distanceOnPath);

      if (point) {
        // Car color
        const color = carColors[index % carColors.length];

        // Car circle (larger, solid)
        carGroup
          .append("circle")
          .attr("cx", point.x)
          .attr("cy", point.y)
          .attr("r", 9)
          .attr("fill", color)
          .attr("stroke", "#041014")
          .attr("stroke-width", 2.5)
          .style("cursor", "pointer")
          .append("title")
          .text(
            `${car.driver_name}\nPosition: ${car.position}\nLap: ${
              car.current_lap
            }\nSpeed: ${car.speed_kmh.toFixed(
              1
            )} km/h\nBattery: ${car.battery_percentage.toFixed(1)}%`
          );

        // Position number inside car
        carGroup
          .append("text")
          .attr("x", point.x)
          .attr("y", point.y + 4)
          .attr("text-anchor", "middle")
          .attr("fill", "#041014")
          .attr("font-size", "11px")
          .attr("font-weight", "bold")
          .text(car.position);

        // Attack mode indicator
        if (car.attack_mode_active) {
          carGroup
            .append("text")
            .attr("x", point.x + 14)
            .attr("y", point.y - 8)
            .attr("text-anchor", "middle")
            .attr("font-size", "18px")
            .attr("fill", "#00E5FF")
            .text("⚡");
        }
      }
    });

    // Title (use viewBox coordinates)
    svg
      .append("text")
      .attr("x", 450)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .attr("fill", "#FFFFFF")
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .text("🏁 Plaksha E-Prix Circuit - Live View");

    // Legend (use viewBox coordinates)
    svg
      .append("text")
      .attr("x", 20)
      .attr("y", 390)
      .attr("fill", "#8B949E")
      .attr("font-size", "10px")
      .text(`${activeCars.length} cars racing • Plaksha: 2.370km • 10 turns`);
  }, [cars, trackLength]);

  return (
    <div
      ref={containerRef}
      className="rounded-lg p-3 md:p-6 w-full"
      style={{ background: "#0A1820", border: "1px solid #142835" }}
    >
      <div className="w-full overflow-x-auto">
        <svg ref={svgRef} className="w-full h-auto min-w-[300px]"></svg>
      </div>
    </div>
  );
}
