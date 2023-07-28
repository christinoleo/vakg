<script lang="ts">
	import { getContext } from 'svelte';
	import { forceSimulation, forceLink, forceManyBody, forceCenter, quadtree } from 'd3';
	import { drag } from 'd3';
	import { select } from 'd3';
	import { NodeI, type EdgeI } from '$lib/model';

	const { data, width, height, xScale } = getContext('LayerCake') as any;

	export let manyBodyStrength = -10;
	export let x = 'x';
	export let y = 'y';
	export let searchRadius: number | undefined = undefined;

	type PosI = { id: number; x: number; y: number };
	type PosLinkI = { id: number; x: number; y: number; source: string; target: string };
	const initialNodes = $data.nodes as NodeI[];
	const initialLinks = $data.links as EdgeI[];

	let nodes: NodeI[];
	$: nodes = $data.nodes as NodeI[];
	let edges: EdgeI[];
	$: edges = $data.edges as EdgeI[];

	const simulation = forceSimulation<PosI, PosLinkI>(
		initialNodes.map((d) => ({ ...d, id: d.identity }))
	);
	const dragger = (el, node) => {
		const d = drag()
			.on('drag', ({ x, y }) => {
				node.fx = x;
				node.fy = y;
			})
			.on('end', () => {
				node.fx = null;
				node.fy = null;
			});
		select(el).call(d);
	};

	simulation.on('tick', () => {
		$data.nodes = simulation.nodes();
		$data.links = initialLinks;
	});

	$: {
		simulation
			.force(
				'link',
				forceLink<PosI, PosLinkI>($data.links).id((d) => d.id)
			)
			.force('charge', forceManyBody().strength(manyBodyStrength))
			.force('center', forceCenter($width / 2, $height / 2))
			.alpha(0.8)
			.restart();
	}

	let found: PosI | undefined;
	function findItem(evt: any) {
		const xLayerKey = `layer${x.toUpperCase()}`;
		const yLayerKey = `layer${y.toUpperCase()}`;

		const xLayerVal = evt[xLayerKey] / (x === 'x' ? $width : $height);
		const yLayerVal = evt[yLayerKey] / (y === 'y' ? $height : $width);

		found =
			(finder.find($xScale(xLayerVal), $xScale(yLayerVal), searchRadius) as PosI) || undefined;
	}

	$: finder = quadtree<{ x: number; y: number }>()
		.extent([
			[-1, -1],
			[$width + 1, $height + 1]
		])
		.x((d) => d.x)
		.y((d) => d.y)
		.addAll($data.nodes);
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<svg on:mousemove={findItem} class="root">
	{#each edges as edge}
		{@const start = nodes.find((n) => n.identity === edge.start)}
		{@const end = nodes.find((n) => n.identity === edge.end)}
		{#if start && end}
			<line class="link" x1={start.x} x2={end.x} y1={start.y} y2={end.y} stroke="black" />
		{/if}
	{/each}
	{#each nodes as point}
		<circle
			use:dragger={point}
			class="node"
			r="5"
			fill={point.identity === found?.id ? 'red' : 'steelblue'}
			cx={point.x}
			cy={point.y}
		/>
	{/each}
</svg>

<style>
	.root {
		width: 100%;
		height: 100%;
	}
</style>
