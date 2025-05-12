<script>
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { config } from '$lib/stores';

	const i18n = getContext('i18n');

	export let saveHandler = () => {};

	// Theme settings
	let primaryColor = '#3B82F6'; // Default blue color
	let secondaryColor = '#10B981'; // Default green color
	let accentColor = '#8B5CF6'; // Default purple color
	let logoUrl = '';
	let faviconUrl = '';
	let customLogoFile = null;
	let customFaviconFile = null;
	let isLoading = false;

	// Load saved settings on mount
	onMount(async () => {
		isLoading = true;
		try {
			// Load theme settings from the server
			const response = await fetch('/api/theme');
			if (response.ok) {
				const themeData = await response.json();
				primaryColor = themeData.primaryColor || primaryColor;
				secondaryColor = themeData.secondaryColor || secondaryColor;
				accentColor = themeData.accentColor || accentColor;
				logoUrl = themeData.logoUrl || logoUrl;
				faviconUrl = themeData.faviconUrl || faviconUrl;
			}
			
			// Apply theme immediately
			applyThemeToDocument();
		} catch (e) {
			console.error('Error loading theme settings:', e);
			// Don't show error toast on initial load, just use defaults
		} finally {
			isLoading = false;
		}
	});

	// Handle file upload for logo
	function handleLogoFileChange(event) {
		const file = event.target.files[0];
		if (file) {
			customLogoFile = file;
			// Create a preview URL for immediate display
			logoUrl = URL.createObjectURL(file);
			
			// Convert file to base64 for storage
			const reader = new FileReader();
			reader.onload = (e) => {
				// Store the base64 data in logoUrl when saving
				const base64Data = e.target.result;
				// Keep the blob URL for preview, but we'll use base64 when saving
				customLogoFile = {
					file: file,
					base64: base64Data
				};
			};
			reader.readAsDataURL(file);
		}
	}

	// Handle file upload for favicon
	function handleFaviconFileChange(event) {
		const file = event.target.files[0];
		if (file) {
			customFaviconFile = file;
			// Create a preview URL for immediate display
			faviconUrl = URL.createObjectURL(file);
			
			// Convert file to base64 for storage
			const reader = new FileReader();
			reader.onload = (e) => {
				// Store the base64 data in faviconUrl when saving
				const base64Data = e.target.result;
				// Keep the blob URL for preview, but we'll use base64 when saving
				customFaviconFile = {
					file: file,
					base64: base64Data
				};
			};
			reader.readAsDataURL(file);
		}
	}

	// Reset logo to default
	function resetLogo() {
		logoUrl = '';
		customLogoFile = null;
		if (document.getElementById('logo-upload')) {
			document.getElementById('logo-upload').value = '';
		}
	}

	// Reset favicon to default
	function resetFavicon() {
		faviconUrl = '';
		customFaviconFile = null;
		if (document.getElementById('favicon-upload')) {
			document.getElementById('favicon-upload').value = '';
		}
	}

	// Save theme settings
	async function saveThemeSettings() {
		isLoading = true;
		try {
			// Prepare theme data
			const themeData = {
				primaryColor,
				secondaryColor,
				accentColor,
				// Use base64 data if available from file upload, otherwise use the URL
				logoUrl: customLogoFile?.base64 || logoUrl,
				faviconUrl: customFaviconFile?.base64 || faviconUrl
			};
			
			// Save to server using our new API endpoint
			const response = await fetch('/api/theme', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(themeData)
			});
			
			if (!response.ok) {
				throw new Error('Failed to save theme settings to server');
			}
			
			// Apply theme to document
			applyThemeToDocument();
			
			// Call the provided saveHandler
			if (typeof saveHandler === 'function') {
				await saveHandler();
			}
			
		} catch (e) {
			console.error('Error saving theme settings:', e);
			toast.error($i18n.t('Failed to save theme settings'));
		} finally {
			isLoading = false;
		}
	}
	
	// Apply theme to document
	function applyThemeToDocument() {
		// Create or update CSS variables in document root
		document.documentElement.style.setProperty('--primary-color', primaryColor);
		document.documentElement.style.setProperty('--secondary-color', secondaryColor);
		document.documentElement.style.setProperty('--accent-color', accentColor);
		
		// Create or update a stylesheet for the theme
		let styleElement = document.getElementById('custom-theme-styles');
		if (!styleElement) {
			styleElement = document.createElement('style');
			styleElement.id = 'custom-theme-styles';
			document.head.appendChild(styleElement);
		}
		
		// Apply CSS rules using the theme colors
		styleElement.textContent = `
			:root {
				--primary-color: ${primaryColor};
				--secondary-color: ${secondaryColor};
				--accent-color: ${accentColor};
			}
			
			/* Buttons */
			.btn-primary, 
			.bg-blue-600,
			.hover\\:bg-blue-700:hover,
			button[type="submit"],
			.bg-blue-500 {
				background-color: var(--primary-color) !important;
			}
			
			/* Text colors */
			.text-blue-600,
			.hover\\:text-blue-700:hover,
			.text-blue-500,
			a.text-blue-500,
			.hover\\:text-blue-500:hover {
				color: var(--primary-color) !important;
			}
			
			/* Border colors */
			.border-blue-600,
			.focus\\:border-blue-500:focus,
			.border-blue-500,
			.hover\\:border-blue-500:hover {
				border-color: var(--primary-color) !important;
			}
			
			/* Focus rings */
			.focus\\:ring-blue-500:focus,
			.focus\\:ring-blue-600:focus,
			.focus\\:ring-offset-blue-200:focus {
				--tw-ring-color: var(--primary-color) !important;
			}
			
			/* Secondary color elements */
			.bg-green-500,
			.hover\\:bg-green-600:hover {
				background-color: var(--secondary-color) !important;
			}
			
			.text-green-500,
			.hover\\:text-green-600:hover {
				color: var(--secondary-color) !important;
			}
			
			/* Accent color elements */
			.bg-purple-500,
			.hover\\:bg-purple-600:hover,
			.bg-indigo-500,
			.hover\\:bg-indigo-600:hover {
				background-color: var(--accent-color) !important;
			}
			
			.text-purple-500,
			.hover\\:text-purple-600:hover,
			.text-indigo-500,
			.hover\\:text-indigo-600:hover {
				color: var(--accent-color) !important;
			}
		`;
		
		// Update logo if provided
		if (logoUrl) {
			const logoElements = document.querySelectorAll('.app-logo, #logo, #logo-her');
			logoElements.forEach(element => {
				if (element instanceof HTMLImageElement) {
					element.src = logoUrl;
				}
			});
		}
		
		// Update favicon if provided
		if (faviconUrl) {
			// Look for existing favicon link
			let faviconLink = document.querySelector('link[rel="icon"]') || 
							  document.querySelector('link[rel="shortcut icon"]');
			
			// If no favicon link exists, create one
			if (!faviconLink) {
				faviconLink = document.createElement('link');
				faviconLink.rel = 'icon';
				document.head.appendChild(faviconLink);
			}
			
			// Update the favicon href
			faviconLink.href = faviconUrl;
		}
	}
</script>

<div class="flex flex-col space-y-4">
	<div class="flex flex-col space-y-2">
		<h2 class="text-xl font-semibold">{$i18n.t('Theme Settings')}</h2>
		<p class="text-sm text-gray-500 dark:text-gray-400">
			{$i18n.t('Customize the appearance of your Open WebUI instance')}
		</p>
	</div>
	
	{#if isLoading}
		<div class="flex justify-center py-8">
			<div class="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
		</div>
	{:else}

	<div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-6">
		<!-- Branding Section -->
		<div class="space-y-6">
			<!-- Logo Section -->
			<div class="space-y-3">
				<h3 class="text-lg font-medium">{$i18n.t('Custom Logo')}</h3>
				<p class="text-sm text-gray-600 dark:text-gray-300">
					{$i18n.t('Upload a custom logo for your instance')}
				</p>
				
				<div class="flex flex-col space-y-4">
					<!-- Logo Upload -->
					<div class="flex flex-col space-y-2">
						<label for="logo-upload" class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$i18n.t('Upload Logo')}
						</label>
						<input
							id="logo-upload"
							type="file"
							accept="image/*"
							on:change={handleLogoFileChange}
							class="block w-full text-sm text-gray-500 dark:text-gray-300
								file:mr-4 file:py-2 file:px-4
								file:rounded-md file:border-0
								file:text-sm file:font-semibold
								file:bg-blue-50 file:text-blue-700
								dark:file:bg-blue-900 dark:file:text-blue-200
								hover:file:bg-blue-100 dark:hover:file:bg-blue-800
								transition"
						/>
					</div>
					
					<!-- Logo URL -->
					<div class="flex flex-col space-y-2">
						<label for="logo-url" class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$i18n.t('Or enter logo URL')}
						</label>
						<input
							id="logo-url"
							type="text"
							bind:value={logoUrl}
							placeholder="https://example.com/logo.png"
							class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>
					
					<!-- Logo Preview -->
					{#if logoUrl}
						<div class="mt-2 p-4 bg-white dark:bg-gray-700 rounded-md flex flex-col items-center justify-center space-y-3">
							<img src={logoUrl} alt="Logo Preview" class="max-h-16 max-w-full" />
							<button 
								on:click={resetLogo}
								class="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
							>
								{$i18n.t('Reset to default')}
							</button>
						</div>
					{/if}
				</div>
			</div>

			<!-- Favicon Section -->
			<div class="space-y-3 pt-4 border-t border-gray-200 dark:border-gray-700">
				<h3 class="text-lg font-medium">{$i18n.t('Custom Favicon')}</h3>
				<p class="text-sm text-gray-600 dark:text-gray-300">
					{$i18n.t('Upload a custom favicon for your instance')}
				</p>
				
				<div class="flex flex-col space-y-4">
					<!-- Favicon Upload -->
					<div class="flex flex-col space-y-2">
						<label for="favicon-upload" class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$i18n.t('Upload Favicon')}
						</label>
						<input
							id="favicon-upload"
							type="file"
							accept="image/*"
							on:change={handleFaviconFileChange}
							class="block w-full text-sm text-gray-500 dark:text-gray-300
								file:mr-4 file:py-2 file:px-4
								file:rounded-md file:border-0
								file:text-sm file:font-semibold
								file:bg-blue-50 file:text-blue-700
								dark:file:bg-blue-900 dark:file:text-blue-200
								hover:file:bg-blue-100 dark:hover:file:bg-blue-800
								transition"
						/>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
							{$i18n.t('Recommended: square image in .ico, .png, or .svg format')}
						</p>
					</div>
					
					<!-- Favicon URL -->
					<div class="flex flex-col space-y-2">
						<label for="favicon-url" class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$i18n.t('Or enter favicon URL')}
						</label>
						<input
							id="favicon-url"
							type="text"
							bind:value={faviconUrl}
							placeholder="https://example.com/favicon.ico"
							class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>
					
					<!-- Favicon Preview -->
					{#if faviconUrl}
						<div class="mt-2 p-4 bg-white dark:bg-gray-700 rounded-md flex flex-col items-center justify-center space-y-3">
							<div class="flex items-center justify-center bg-gray-100 dark:bg-gray-800 p-2 rounded-md">
								<img src={faviconUrl} alt="Favicon Preview" class="h-8 w-8" />
								<span class="ml-2 text-sm text-gray-600 dark:text-gray-300">Tab icon preview</span>
							</div>
							<button 
								on:click={resetFavicon}
								class="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
							>
								{$i18n.t('Reset to default')}
							</button>
						</div>
					{/if}
				</div>
			</div>
		</div>
		
		<!-- Colors Section -->
		<div class="space-y-3 pt-2 border-t border-gray-200 dark:border-gray-700">
			<h3 class="text-lg font-medium">{$i18n.t('Theme Colors')}</h3>
			<p class="text-sm text-gray-600 dark:text-gray-300">
				{$i18n.t('Customize the colors of the interface')}
			</p>
			
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Primary Color -->
				<div class="flex flex-col space-y-2">
					<label for="primary-color" class="text-sm font-medium text-gray-700 dark:text-gray-300">
						{$i18n.t('Primary Color')}
					</label>
					<div class="flex items-center space-x-2">
						<input
							id="primary-color"
							type="color"
							bind:value={primaryColor}
							class="h-10 w-10 border-0 rounded-md cursor-pointer"
						/>
						<input
							type="text"
							bind:value={primaryColor}
							class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>
				</div>
				
				<!-- Secondary Color -->
				<div class="flex flex-col space-y-2">
					<label for="secondary-color" class="text-sm font-medium text-gray-700 dark:text-gray-300">
						{$i18n.t('Secondary Color')}
					</label>
					<div class="flex items-center space-x-2">
						<input
							id="secondary-color"
							type="color"
							bind:value={secondaryColor}
							class="h-10 w-10 border-0 rounded-md cursor-pointer"
						/>
						<input
							type="text"
							bind:value={secondaryColor}
							class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>
				</div>
				
				<!-- Accent Color -->
				<div class="flex flex-col space-y-2">
					<label for="accent-color" class="text-sm font-medium text-gray-700 dark:text-gray-300">
						{$i18n.t('Accent Color')}
					</label>
					<div class="flex items-center space-x-2">
						<input
							id="accent-color"
							type="color"
							bind:value={accentColor}
							class="h-10 w-10 border-0 rounded-md cursor-pointer"
						/>
						<input
							type="text"
							bind:value={accentColor}
							class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>
				</div>
			</div>
			
			<!-- Color Preview -->
			<div class="mt-4 p-4 bg-white dark:bg-gray-700 rounded-md">
				<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
					{$i18n.t('Preview')}
				</h4>
				<div class="flex flex-wrap gap-3">
					<div class="flex flex-col items-center">
						<div
							class="h-12 w-12 rounded-md"
							style="background-color: {primaryColor};"
							aria-label="Primary color preview"
						></div>
						<span class="text-xs mt-1 text-gray-600 dark:text-gray-400">Primary</span>
					</div>
					<div class="flex flex-col items-center">
						<div
							class="h-12 w-12 rounded-md"
							style="background-color: {secondaryColor};"
							aria-label="Secondary color preview"
						></div>
						<span class="text-xs mt-1 text-gray-600 dark:text-gray-400">Secondary</span>
					</div>
					<div class="flex flex-col items-center">
						<div
							class="h-12 w-12 rounded-md"
							style="background-color: {accentColor};"
							aria-label="Accent color preview"
						></div>
						<span class="text-xs mt-1 text-gray-600 dark:text-gray-400">Accent</span>
					</div>
				</div>
				
				<!-- Sample UI Elements -->
				<div class="mt-4 border-t border-gray-200 dark:border-gray-600 pt-4">
					<h5 class="text-xs font-medium mb-2 text-gray-700 dark:text-gray-300">
						{$i18n.t('UI Elements Preview')}
					</h5>
					
					<!-- Buttons -->
					<div class="flex flex-wrap gap-3 mb-3">
						<button
							class="px-3 py-1.5 text-sm font-medium rounded-md text-white"
							style="background-color: {primaryColor};"
						>
							{$i18n.t('Primary Button')}
						</button>
						<button
							class="px-3 py-1.5 text-sm font-medium rounded-md text-white"
							style="background-color: {secondaryColor};"
						>
							{$i18n.t('Secondary Button')}
						</button>
						<button
							class="px-3 py-1.5 text-sm font-medium rounded-md text-white"
							style="background-color: {accentColor};"
						>
							{$i18n.t('Accent Button')}
						</button>
					</div>
					
					<!-- Links and Text -->
					<div class="flex flex-wrap gap-3 mb-3">
						<a href="#" class="text-sm" style="color: {primaryColor};">
							{$i18n.t('Primary Link')}
						</a>
						<a href="#" class="text-sm" style="color: {secondaryColor};">
							{$i18n.t('Secondary Link')}
						</a>
						<a href="#" class="text-sm" style="color: {accentColor};">
							{$i18n.t('Accent Link')}
						</a>
					</div>
					
					<!-- Form Elements -->
					<div class="flex flex-wrap gap-3 mb-3">
						<div class="flex items-center">
							<input 
								type="checkbox" 
								class="rounded" 
								style="accent-color: {primaryColor};"
								checked
							/>
							<span class="ml-1 text-xs">{$i18n.t('Checkbox')}</span>
						</div>
						<div class="flex items-center">
							<input 
								type="radio" 
								class="rounded-full" 
								style="accent-color: {primaryColor};"
								checked
							/>
							<span class="ml-1 text-xs">{$i18n.t('Radio')}</span>
						</div>
						<div class="w-24">
							<div class="h-1 rounded-full" style="background-color: {primaryColor};">
							</div>
							<span class="text-xs">{$i18n.t('Progress')}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<div class="flex justify-end">
		<button
			on:click={saveThemeSettings}
			disabled={isLoading}
			class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{#if isLoading}
				<span class="inline-block animate-spin mr-2">⟳</span>
			{/if}
			{$i18n.t('Save')}
		</button>
	</div>
	{/if}
</div>
