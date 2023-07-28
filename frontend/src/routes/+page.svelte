<script lang="ts">
	import type { EdgeI, NodeI } from '$lib/model';
	import NodeLink from '$lib/viz/components/NodeLink.svelte';
	import QuadTree from '$lib/viz/components/QuadTree.html.svelte';
	// Node-link diagram in layercake.graphics
	// as seen on:
	// https://jandot.github.io/posts/nodelink-in-layercake/
	// https://vis.social/@jandot
	import { Html, LayerCake, Svg } from 'layercake';
	let data: { nodes: NodeI[]; edges: EdgeI[] } = {
		nodes: [
			{ identity: 1, labels: ['a'], x: 1, y: 1, properties: {} },
			{ identity: 2, labels: ['b'], x: 0, y: 2, properties: {} },
			{ identity: 3, labels: ['c'], x: 1, y: 3, properties: {} },
			{ identity: 4, labels: ['d'], x: 0, y: 4, properties: {} },
			{ identity: 5, labels: ['e'], x: 1, y: 5, properties: {} }
		],
		edges: [
			{ start: 1, end: 2, identity: 1, properties: {} },
			{ start: 1, end: 3, identity: 2, properties: {} },
			{ start: 2, end: 3, identity: 3, properties: {} },
			{ start: 3, end: 4, identity: 4, properties: {} },
			{ start: 3, end: 5, identity: 5, properties: {} }
		]
	};
</script>

<div class="chart-container">
	<LayerCake {data} x={'x'} y={'y'} flatData={data.nodes}>
		<NodeLink />
		<!-- <Html>
			<QuadTree dataset={data.nodes} let:x let:y let:visible>
				<div class="circle" style="top:{y}px;left:{x}px;display: {visible ? 'block' : 'none'};" />
			</QuadTree>
		</Html> -->
	</LayerCake>
</div>

<style>
	.chart-container {
		width: 600px;
		height: 600px;
	}

	.circle {
		position: absolute;
		border-radius: 50%;
		background-color: rgba(171, 0, 214);
		transform: translate(-50%, -50%);
		pointer-events: none;
		width: 10px;
		height: 10px;
	}
</style>
