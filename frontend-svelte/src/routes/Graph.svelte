<script lang="ts">
	export let depth = 0;
	export let xpos = 0;
	export let ypos = 0;
	export let message = 'hi';
	let width = Math.floor(1000 * (1 / Math.pow(2, depth)));
	let styles = {
		top: `${xpos}`,
		left: `${ypos}`,
		width: `${width}px`,
		height: `${width}px`
	};
	$: cssVarStyles = Object.entries(styles)
		.map(([key, value]) => `--${key}:${value}`)
		.join(';');
	let max_depth = 3;
	type Node = [number, number, string];
	let nodes: Node[] = [
		[10, 10, 'a'],
		[20, 20, 'b'],
		[30, 100, 'c']
	];
	// let edges: [number, number][] = [];
</script>

<div class="graph" style={cssVarStyles}>
	{message}
	{#if depth < max_depth}
		{#each nodes as [x, y, msg]}
			<svelte:self depth={depth + 1} message={msg} xpos={x} ypos={y} />
		{/each}
	{/if}
</div>

<style>
	.graph {
		position: absolute;
		width: 500px;
		height: 500px;
		/* border-top: 1px solid rgba(0, 0, 0, 0.1); */
		/* border-bottom: 1px solid rgba(0, 0, 0, 0.1); */
		/* margin: 1rem 0; */
	}
</style>
