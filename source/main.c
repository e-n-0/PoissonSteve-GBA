#include <gba_console.h>
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <gba_types.h>

#include <stdio.h>
#include <stdlib.h>

// Include our converted animation
#include "animation.h"

// Define some basic colors
#define RGB16(r,g,b)  ((r)+((g)<<5)+((b)<<10))
#define RED     RGB16(31,0,0)
#define GREEN   RGB16(0,31,0)
#define BLUE    RGB16(0,0,31)
#define BLACK   RGB16(0,0,0)
#define WHITE   RGB16(31,31,31)

// Function prototypes
void drawFrame(u16 frameIndex);
void updateAnimation(void);

// Animation variables
u16 currentFrame = 0;
u16 frameTimer = 0;
bool playingAnimation = true;

//---------------------------------------------------------------------------------
// Program entry point
//---------------------------------------------------------------------------------
int main(void) {
//---------------------------------------------------------------------------------
	// Initialize interrupts
	irqInit();
	irqEnable(IRQ_VBLANK);
	
	// Set Mode 3 (16-bit color, bitmap mode)
	SetMode(MODE_3 | BG2_ENABLE);
	
	// Clear screen to black
	u16* videoBuffer = (u16*)MODE3_FB;
	for (int i = 0; i < 240 * 160; i++) {
		videoBuffer[i] = BLACK;
	}
	
	// Draw the first frame of the animation
	drawFrame(0);
	
	// Main loop
	while (1) {
		// Wait for VBlank
		VBlankIntrWait();
		
		// Poll for button presses
		scanKeys();
		u16 keys = keysDown();
		
		// Handle input
		if (keys & KEY_A) {
			// A button pressed - toggle between animation and color bars
			playingAnimation = false;
			
			// Draw color bars
			for (int y = 0; y < 160; y++) {
				for (int x = 0; x < 240; x++) {
					int pos = y * 240 + x;
					
					if (x < 80)
						videoBuffer[pos] = RED;
					else if (x < 160)
						videoBuffer[pos] = GREEN;
					else
						videoBuffer[pos] = BLUE;
				}
			}
		}
		
		if (keys & KEY_B) {
			// B button pressed - restore animation and reset to first frame
			playingAnimation = true;
			currentFrame = 0;
			frameTimer = 0;
			drawFrame(currentFrame);
		}
		
		// Update animation if playing
		if (playingAnimation) {
			updateAnimation();
		}
	}
	
	return 0;
}

// Draw a specific frame of the animation to the screen
void drawFrame(u16 frameIndex) {
	// Check if frame exists
	if (frameIndex >= poisson_frame_count) {
		return;
	}
	
	u16* videoBuffer = (u16*)MODE3_FB;
	const u16* frameData = poisson_frames[frameIndex];
	
	// Copy frame data to screen
	for (int i = 0; i < 240 * 160; i++) {
		videoBuffer[i] = frameData[i];
	}
}

// Update animation state
void updateAnimation() {
	// For now, in case of 1-frame animation, we do nothing
	if (poisson_frame_count <= 1) {
		return;
	}
	
	// Increment frame timer
	frameTimer++;
	
	// Check if it's time to advance to the next frame
	if (frameTimer >= poisson_durations[currentFrame]) {
		frameTimer = 0;
		currentFrame++;
		
		// Loop back to first frame if we reached the end
		if (currentFrame >= poisson_frame_count) {
			currentFrame = 0;
		}
		
		// Draw the new frame
		drawFrame(currentFrame);
	}
}


