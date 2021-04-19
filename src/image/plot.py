import cv2

def show_imgs(imgs:list):
    
    for i, img in enumerate(imgs):
        cv2.imshow(f"Image #{i}",img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()