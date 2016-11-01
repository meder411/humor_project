function box = tlwh2xyxy(box)
	box = [box(1), box(2), box(1) + box(3), box(2) + box(4)];
