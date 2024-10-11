try:
    from OpenGL.GL import *
    from glfw.GLFW import *

    from glfw import _GLFWwindow as GLFWwindow

    from PIL import Image

    import glm
except ImportError:
    import requirements

    from OpenGL.GL import *
    from glfw.GLFW import *

    from glfw import _GLFWwindow as GLFWwindow

    from PIL import Image

    import glm

from shader_s import Shader

import platform, ctypes, os

# the relative path where the textures are located
IMAGE_RESOURCE_PATH = "../../../resources/textures/"

# function that loads and automatically flips an image vertically
LOAD_IMAGE = lambda name: Image.open(os.path.join(IMAGE_RESOURCE_PATH, name)).transpose(Image.FLIP_TOP_BOTTOM)

# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600

# stores how much we're seeing of either texture
mixValue = 0.2

def main() -> int:

    # glfw: initialize and configure
    # ------------------------------
    glfwInit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    if (platform.system() == "Darwin"): # APPLE
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    # glfw window creation
    # --------------------
    window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", None, None)
    if (window == None):

        print("Failed to create GLFW window")
        glfwTerminate()
        return -1

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)

    # build and compile our shader zprogram
    # ------------------------------------
    ourShader = Shader("4.5.texture.vs", "4.5.texture.fs")

    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    vertices = glm.array(glm.float32,
        # positions          # colors           # texture coords
         0.5,  0.5, 0.0,   1.0, 0.0, 0.0,   1.0, 1.0, # top right
         0.5, -0.5, 0.0,   0.0, 1.0, 0.0,   1.0, 0.0, # bottom right
        -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0, # bottom left
        -0.5,  0.5, 0.0,   1.0, 1.0, 0.0,   0.0, 1.0  # top left
    )

    indices = glm.array(glm.uint32,
        0, 1, 3, # first triangle
        1, 2, 3  # second triangle
    )

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices.ptr, GL_STATIC_DRAW)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)
    # color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)
    # texture coord attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(2)


    # load and create a texture 
    # -------------------------
    # texture 1
    # ---------
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)	# set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image, create texture and generate mipmaps
    try:
        img = LOAD_IMAGE("container.jpg")

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

        img.close()

    except:

        print("Failed to load texture")
        
    # texture 2
    # ---------
    texture2 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture2)
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)	# set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image, create texture and generate mipmaps
    try:
        img = LOAD_IMAGE("awesomeface.png")

        # note that the awesomeface.png has transparency and thus an alpha channel, so make sure to tell OpenGL the data type is of GL_RGBA
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

        img.close()

    except:

        print("Failed to load texture")

    # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
    # -------------------------------------------------------------------------------------------
    ourShader.use() # don't forget to activate/use the shader before setting uniformsnot 
    # either set it manually like so:
    glUniform1i(glGetUniformLocation(ourShader.ID, "texture1"), 0)
    # or set it via the texture class
    ourShader.setInt("texture2", 1)


    # render loop
    # -----------
    while (not glfwWindowShouldClose(window)):

        # input
        # -----
        processInput(window)

        # render
        # ------
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # bind textures on corresponding texture units
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture2)

        # set the texture mix value in the shader
        ourShader.setFloat("mixValue", mixValue)

        # render container
        ourShader.use()
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (VAO,))
    glDeleteBuffers(1, (VBO,))
    glDeleteBuffers(1, (EBO,))

    # glfw: terminate, clearing all previously allocated GLFW resources.
    # ------------------------------------------------------------------
    glfwTerminate()
    return 0

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:
    global mixValue

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS):
        glfwSetWindowShouldClose(window, True)

    if (glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS):

        mixValue += 0.001 # change this value accordingly (might be too slow or too fast based on system hardware)
        if(mixValue >= 1.0):
            mixValue = 1.0

    if (glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS):

        mixValue -= 0.001 # change this value accordingly (might be too slow or too fast based on system hardware)
        if (mixValue <= 0.0):
            mixValue = 0.0


# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)


main()