// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// while(1){
//    if(keyboardPressed){
//      for(eachPixel){
//        ColorPixelBlack();
//      }
//    }else{
//      for(eachPixel){
//        ColorPixelWhite();
//      }
//    }
//  }

    @point
    M = 0

  (LOOP)
    @KBD
    D = M
    @NOPRESSWHITE
    D;JEQ
    @PRESSBLACK
    0;JMP

  (NOPRESSWHITE)
    (WHITELOOP)
        @place
        D=M
        @LOOP
        D;JLT
        @place
        D=M
        @SCREEN
        A=A+D
        M=0 
        @place
        M=M-1
        @WHITELOOP
        0;JMP
  (PRESSBLACK)
    (BLACKLOOP)
        @place
        D=M
        @8192
        D = A - D
        @LOOP
        D;JLE
        @place
        D=M
        @SCREEN
        A = A + D
        M = -1
        @place
        M = M + 1 
        @BLACKLOOP
        0;JMP

  (END)
    @END
    0,JMP
