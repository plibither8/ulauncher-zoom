EXT_NAME:=com.github.plibither8.ulauncher-zoom
EXT_DIR:=$(shell pwd)

link: 
	ln -s ${EXT_DIR} ~/.local/share/ulauncher/extensions/${EXT_NAME}

dev: 
	ulauncher --no-extensions --dev -v |& grep "ulauncher-zoom"

.PHONY: link dev 
