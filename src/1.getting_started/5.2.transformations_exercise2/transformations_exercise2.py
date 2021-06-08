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
    ourShader = Shader("5.2.transform.vs", "5.2.transform.fs")

    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    vertices = glm.array(glm.float32,
        # positions           # texture coords
         0.5,  0.5, 0.0,    1.0, 1.0, # top right
         0.5, -0.5, 0.0,    1.0, 0.0, # bottom right
        -0.5, -0.5, 0.0,    0.0, 0.0, # bottom left
        -0.5,  0.5, 0.0,    0.0, 1.0  # top left
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)
    # texture coord attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)


    # load and create a texture 
    # -------------------------
    # texture 1
    # ---------
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
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
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)	
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
    ourShader.use()
    ourShader.setInt("texture1", 0)
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


        transform = glm.mat4(1.0) # make sure to initialize matrix to identity matrix first
        # first container
        # ---------------
        transform = glm.translate(transform, glm.vec3(0.5, -0.5, 0.0))
        transform = glm.rotate(transform, glfwGetTime(), glm.vec3(0.0, 0.0, 1.0))
        # get their uniform location and set matrix (using glm::value_ptr)
        transformLoc = glGetUniformLocation(ourShader.ID, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(transform))

        # with the uniform matrix set, draw the first container
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # second transformation
        # ---------------------
        transform = glm.mat4(1.0) # reset it to identity matrix
        transform = glm.translate(transform, glm.vec3(-0.5, 0.5, 0.0))
        scaleAmount = glm.sin(glfwGetTime())
        transform = glm.scale(transform, glm.vec3(scaleAmount, scaleAmount, scaleAmount))
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(transform)) 

        # now with the uniform matrix being replaced with new transformations, draw it again.
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

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS):
        glfwSetWindowShouldClose(window, True)

# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)


main()