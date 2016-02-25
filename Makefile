SRC1=	meta.py
SRC2=	shown.py
TARG1=	meta
TARG2=	shown
SRCS= $(SRC1) $(SRC2)
DEST=	~/bin
DATA2=	/images/media/Doctor\ Who/Season\ 19* 
TEST2=	Doctor.Who.meta
TESTS=	$(TEST2)

INSTALL=	/usr/bin/install
OWNER=	peter
GROUP=	users
MODE=	755

default:
	@echo "Please choose an action."

install:	$(SRCS)
	$(INSTALL) -o $(OWNER) -g $(GROUP) -m $(MODE) -p $(SRC1) $(DEST)/$(TARG1)
	$(INSTALL) -o $(OWNER) -g $(GROUP) -m $(MODE) -p $(SRC2) $(DEST)/$(TARG2)

test:	$(SRC2) $(TESTS)
	python $(SRC2) -d $(DATA2)| sed 's?.*/.??' | sort -t : +1 | tee $(TEST2)
