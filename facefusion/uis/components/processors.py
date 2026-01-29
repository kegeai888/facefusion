from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.filesystem import get_file_name, resolve_file_paths
from facefusion.processors.core import get_processors_modules
from facefusion.uis.core import register_ui_component

PROCESSORS_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None


def render() -> None:
	global PROCESSORS_CHECKBOX_GROUP

	processor_choices = get_processor_choices(state_manager.get_item('processors'))

	PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label = translator.get('uis.processors_checkbox_group'),
		choices = processor_choices,
		value = state_manager.get_item('processors')
	)
	register_ui_component('processors_checkbox_group', PROCESSORS_CHECKBOX_GROUP)


def listen() -> None:
	PROCESSORS_CHECKBOX_GROUP.change(update_processors, inputs = PROCESSORS_CHECKBOX_GROUP, outputs = PROCESSORS_CHECKBOX_GROUP)


def update_processors(processors : List[str]) -> gradio.CheckboxGroup:
	# processors already contains internal IDs (not translated names) when using tuple choices
	for processor_module in get_processors_modules(state_manager.get_item('processors')):
		if hasattr(processor_module, 'clear_inference_pool'):
			processor_module.clear_inference_pool()

	for processor_module in get_processors_modules(processors):
		if not processor_module.pre_check():
			return gradio.CheckboxGroup()

	state_manager.set_item('processors', processors)
	processor_choices = get_processor_choices(state_manager.get_item('processors'))
	return gradio.CheckboxGroup(value = state_manager.get_item('processors'), choices = processor_choices)


def sort_processors(processors : List[str]) -> List[str]:
	available_processors = [ get_file_name(file_path) for file_path in resolve_file_paths('facefusion/processors/modules') ]
	current_processors = []

	for processor in processors + available_processors:
		if processor in available_processors and processor not in current_processors:
			current_processors.append(processor)

	return current_processors


def translate_processors(processors : List[str]) -> List[str]:
	"""Translate processor IDs to display names"""
	translated = []
	for processor in processors:
		translated_name = translator.get(f'uis.{processor}')
		if translated_name and translated_name != f'uis.{processor}':
			translated.append(translated_name)
		else:
			translated.append(processor)
	return translated


def untranslate_processors(translated_processors : List[str]) -> List[str]:
	"""Convert translated display names back to processor IDs"""
	available_processors = [ get_file_name(file_path) for file_path in resolve_file_paths('facefusion/processors/modules') ]
	processor_map = {}

	# Build reverse mapping from translated names to IDs
	for processor_id in available_processors:
		translated_name = translator.get(f'uis.{processor_id}')
		if translated_name and translated_name != f'uis.{processor_id}':
			processor_map[translated_name] = processor_id
		processor_map[processor_id] = processor_id  # Also map ID to itself

	# Convert translated names back to IDs
	processor_ids = []
	for name in translated_processors:
		processor_id = processor_map.get(name, name)
		processor_ids.append(processor_id)

	return processor_ids


def get_processor_choices(processors : List[str]) -> List[Tuple[str, str]]:
	"""Get processor choices as (display_name, value) tuples"""
	sorted_processors = sort_processors(processors)
	choices = []

	for processor_id in sorted_processors:
		translated_name = translator.get(f'uis.{processor_id}')
		if translated_name and translated_name != f'uis.{processor_id}':
			choices.append((translated_name, processor_id))
		else:
			choices.append((processor_id, processor_id))

	return choices
