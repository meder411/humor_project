function box = points2xyxy(box)
	box = [min(box(:,1)), min(box(:,2)), max(box(:,1)), max(box(:,2))];
