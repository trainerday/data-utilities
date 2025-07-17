import { App, Editor, MarkdownView, Notice, Plugin, PluginSettingTab, Setting, TFile } from 'obsidian';

interface ImgBBSettings {
	apiKey: string;
	autoUpload: boolean;
	deleteLocalAfterUpload: boolean;
}

const DEFAULT_SETTINGS: ImgBBSettings = {
	apiKey: 'b53de65dae499fbb17ef3cc4e274e145',
	autoUpload: true,
	deleteLocalAfterUpload: true
}

export default class ImgBBUploaderPlugin extends Plugin {
	settings: ImgBBSettings;

	async onload() {
		await this.loadSettings();

		// Add ribbon icon for manual upload
		this.addRibbonIcon('image', 'Upload Images to ImgBB', (evt: MouseEvent) => {
			this.uploadImagesInActiveFile();
		});

		// Add command for manual upload
		this.addCommand({
			id: 'upload-images-to-imgbb',
			name: 'Upload all images in current file to ImgBB',
			callback: () => {
				this.uploadImagesInActiveFile();
			}
		});

		// Add command to upload single image
		this.addCommand({
			id: 'upload-selected-image',
			name: 'Upload selected image to ImgBB',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.uploadSelectedImage(editor);
			}
		});

		// Listen for file modifications to auto-upload
		if (this.settings.autoUpload) {
			this.registerEvent(
				this.app.vault.on('modify', (file) => {
					if (file instanceof TFile && file.extension === 'md') {
						// Delay to allow file to be fully written
						setTimeout(() => {
							this.processFileForImages(file);
						}, 1000);
					}
				})
			);
		}

		// Add settings tab
		this.addSettingTab(new ImgBBSettingTab(this.app, this));
	}

	async uploadImagesInActiveFile() {
		const activeView = this.app.workspace.getActiveViewOfType(MarkdownView);
		if (!activeView) {
			new Notice('No active markdown file');
			return;
		}

		const file = activeView.file;
		if (!file) {
			new Notice('No file selected');
			return;
		}

		await this.processFileForImages(file);
	}

	async uploadSelectedImage(editor: Editor) {
		const selection = editor.getSelection();
		const cursor = editor.getCursor();
		
		// Check if selection contains image markdown
		const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/;
		const match = selection.match(imageRegex);
		
		if (match) {
			const [fullMatch, altText, imagePath] = match;
			if (!imagePath.startsWith('http')) {
				// It's a local image, upload it
				const newUrl = await this.uploadLocalImage(imagePath, altText);
				if (newUrl) {
					editor.replaceSelection(`![${altText}](${newUrl})`);
					new Notice('Image uploaded and link replaced!');
				}
			} else {
				new Notice('Image is already a remote URL');
			}
		} else {
			new Notice('Please select an image markdown link first');
		}
	}

	async processFileForImages(file: TFile) {
		if (!this.settings.apiKey) {
			new Notice('Please set your ImgBB API key in settings');
			return;
		}

		const content = await this.app.vault.read(file);
		const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
		let matches = [];
		let match;

		while ((match = imageRegex.exec(content)) !== null) {
			matches.push({
				fullMatch: match[0],
				altText: match[1],
				imagePath: match[2],
				index: match.index
			});
		}

		// Filter for local images only
		const localImages = matches.filter(img => 
			!img.imagePath.startsWith('http') && 
			!img.imagePath.startsWith('https')
		);

		if (localImages.length === 0) {
			return; // No local images to upload
		}

		new Notice(`Found ${localImages.length} local images. Uploading...`);

		let newContent = content;
		let uploadCount = 0;

		// Process images in reverse order to maintain string indices
		for (let i = localImages.length - 1; i >= 0; i--) {
			const img = localImages[i];
			const newUrl = await this.uploadLocalImage(img.imagePath, img.altText);
			
			if (newUrl) {
				const newMarkdown = `![${img.altText}](${newUrl})`;
				newContent = newContent.substring(0, img.index) + newMarkdown + newContent.substring(img.index + img.fullMatch.length);
				uploadCount++;
			}
		}

		if (uploadCount > 0) {
			await this.app.vault.modify(file, newContent);
			new Notice(`Successfully uploaded ${uploadCount} images!`);
		}
	}

	async uploadLocalImage(imagePath: string, altText: string): Promise<string | null> {
		try {
			// Get the file from vault
			const imageFile = this.app.vault.getAbstractFileByPath(imagePath);
			
			if (!imageFile || !(imageFile instanceof TFile)) {
				// Try relative to current file
				const activeView = this.app.workspace.getActiveViewOfType(MarkdownView);
				if (activeView && activeView.file) {
					const currentDir = activeView.file.parent?.path || '';
					const fullPath = currentDir ? `${currentDir}/${imagePath}` : imagePath;
					const relativeFile = this.app.vault.getAbstractFileByPath(fullPath);
					
					if (relativeFile && relativeFile instanceof TFile) {
						return await this.uploadFileToImgBB(relativeFile, altText);
					}
				}
				
				console.warn(`Image file not found: ${imagePath}`);
				return null;
			}

			return await this.uploadFileToImgBB(imageFile as TFile, altText);
		} catch (error) {
			console.error('Error uploading image:', error);
			new Notice(`Failed to upload image: ${imagePath}`);
			return null;
		}
	}

	async uploadFileToImgBB(file: TFile, altText: string): Promise<string | null> {
		try {
			// Read file as array buffer
			const arrayBuffer = await this.app.vault.readBinary(file);
			
			// Convert to base64
			const bytes = new Uint8Array(arrayBuffer);
			let binary = '';
			for (let i = 0; i < bytes.byteLength; i++) {
				binary += String.fromCharCode(bytes[i]);
			}
			const base64 = btoa(binary);

			// Upload to ImgBB
			const formData = new FormData();
			formData.append('key', this.settings.apiKey);
			formData.append('image', base64);
			formData.append('name', altText || file.name);

			const response = await fetch('https://api.imgbb.com/1/upload', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (result.success) {
				// Delete local file if setting is enabled
				if (this.settings.deleteLocalAfterUpload) {
					await this.app.vault.delete(file);
				}
				
				return result.data.url;
			} else {
				throw new Error(result.error?.message || 'Upload failed');
			}
		} catch (error) {
			console.error('ImgBB upload error:', error);
			new Notice(`Upload failed: ${error.message}`);
			return null;
		}
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}

class ImgBBSettingTab extends PluginSettingTab {
	plugin: ImgBBUploaderPlugin;

	constructor(app: App, plugin: ImgBBUploaderPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();

		new Setting(containerEl)
			.setName('ImgBB API Key')
			.setDesc('Your ImgBB API key for uploading images')
			.addText(text => text
				.setPlaceholder('Enter your ImgBB API key')
				.setValue(this.plugin.settings.apiKey)
				.onChange(async (value) => {
					this.plugin.settings.apiKey = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Auto Upload')
			.setDesc('Automatically upload images when files are modified')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.autoUpload)
				.onChange(async (value) => {
					this.plugin.settings.autoUpload = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Delete Local Images')
			.setDesc('Delete local image files after successful upload')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.deleteLocalAfterUpload)
				.onChange(async (value) => {
					this.plugin.settings.deleteLocalAfterUpload = value;
					await this.plugin.saveSettings();
				}));

		// Add instructions
		containerEl.createEl('h3', { text: 'How to use:' });
		containerEl.createEl('p', { text: '1. Paste or drag images into your markdown files' });
		containerEl.createEl('p', { text: '2. Images will be automatically uploaded if Auto Upload is enabled' });
		containerEl.createEl('p', { text: '3. Or use the ribbon icon or command palette to upload manually' });
		containerEl.createEl('p', { text: '4. Local image links will be replaced with ImgBB URLs' });
	}
}