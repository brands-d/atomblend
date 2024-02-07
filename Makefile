zip:
	@cd .. && zip -r blentom/blentom.zip blentom -x "*.gitignore*" -x "*__pycache__*" -x "*blender*" -x "*.git*" -x "*.vscode*" -x "*demo*" -x "*.DS_Store*" -x "*Makefile*" -x "*blentom.zip*" -x "*venv*" -x "*.readthedocs.yml*" -x "*docs*" -x "*blender*" 
