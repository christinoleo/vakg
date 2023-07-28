export type neo4jNode = {
	identity: number;
	labels: string[];
	properties: Record<string, string>;
};

export type neo4jRelationship = {
	identity: number;
	start: number;
	end: number;
	properties: Record<string, string>;
};

export type PosI = {
	x: number;
	y: number;
};

export type NodeI = PosI & neo4jNode;
export type EdgeI = neo4jRelationship;
