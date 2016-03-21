SRC1=	meta.py
SRC2=	shown.py
TARG1=	meta
TARG2=	shown
SRCS= $(SRC1) $(SRC2)
DEST=	~/bin
DATA2=	/images/media/Doctor\ Who/Season\ 19* 
TEST2=	Doctor.Who.meta
META2a= 2015-07-01
TEST2a=	Doctor.Who-$(META2a).meta
TESTS=	$(TEST2) $(TEST2a)

INSTALL=	/usr/bin/install
OWNER=	peter
GROUP=	users
MODE=	755

default:
	@echo "Please choose an action."

install:	$(SRCS)
	$(INSTALL) -o $(OWNER) -g $(GROUP) -m $(MODE) -p $(SRC1) $(DEST)/$(TARG1)
	$(INSTALL) -o $(OWNER) -g $(GROUP) -m $(MODE) -p $(SRC2) $(DEST)/$(TARG2)

test:	$(SRC2)
	python $(SRC2) -d $(DATA2)| sed 's?.*/.??' | sort -t : +1 | tee $(TEST2)
	python $(SRC2) -M $(META2a) -d $(DATA2)| sed 's?.*/.??' | sort -t : +1 | tee $(TEST2a)
